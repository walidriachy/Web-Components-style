#!/usr/bin/env node
/* Runtime-verify components in headless Chrome. No dependencies (Node 22+).

     node tools/verify.mjs                                   every component in components.js
     node tools/verify.mjs --only apt-,dlg-                  ids starting with these prefixes
     node tools/verify.mjs --src components-src/1600-x.json  one batch file, before it is built
     node tools/verify.mjs --clicks                          also click every control; report dead ones
     node tools/verify.mjs --json                            print the full result as JSON

   Exits 1 when anything mounts with an error, throws later, renders blank, has a dead
   control, a placeholder link or a form that would reload the page. Set CHROME=/path to
   use a specific browser binary. */
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const argv = process.argv.slice(2);
const flag = (n) => argv.includes(n);
const opt = (n) => { const i = argv.indexOf(n); return i > -1 ? argv[i + 1] : undefined; };
const TIMEOUT = Number(opt('--timeout') || 1800) * 1000;

function findChrome() {
  const c = [process.env.CHROME,
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'].filter(Boolean);
  for (const p of c) if (fs.existsSync(p)) return p;
  const pw = path.join(os.homedir(), 'Library/Caches/ms-playwright');
  if (fs.existsSync(pw)) {
    for (const d of fs.readdirSync(pw).filter((d) => d.startsWith('chromium')).sort().reverse()) {
      for (const sub of ['chrome-mac/Chromium.app/Contents/MacOS/Chromium',
                         'chrome-mac-arm64/Chromium.app/Contents/MacOS/Chromium',
                         'chrome-headless-shell-mac-arm64/chrome-headless-shell',
                         'chrome-headless-shell-mac-x64/chrome-headless-shell']) {
        const p = path.join(pw, d, sub); if (fs.existsSync(p)) return p;
      }
    }
  }
  throw new Error('No Chrome found. Set CHROME=/path/to/chrome');
}

const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.css': 'text/css' };
function serve() {
  return new Promise((resolve) => {
    const srv = http.createServer((req, res) => {
      const u = decodeURIComponent(new URL(req.url, 'http://x').pathname);
      const f = path.join(ROOT, u);
      if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
      res.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream', 'cache-control': 'no-store' });
      fs.createReadStream(f).pipe(res);
    });
    srv.listen(0, '127.0.0.1', () => resolve(srv));
  });
}

function launch(chrome) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'verify-chrome-'));
  const proc = spawn(chrome, ['--headless=new', '--remote-debugging-port=0', '--user-data-dir=' + dir,
    '--no-first-run', '--no-default-browser-check', '--window-size=1400,1000', '--hide-scrollbars',
    '--disable-background-timer-throttling', '--disable-renderer-backgrounding',
    '--disable-backgrounding-occluded-windows', 'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });
  return new Promise((resolve, reject) => {
    let buf = '';
    const t = setTimeout(() => reject(new Error('Chrome did not start')), 20000);
    proc.stderr.on('data', (d) => {
      buf += d;
      const m = /DevTools listening on (ws:\/\/\S+)/.exec(buf);
      if (m) { clearTimeout(t); resolve({ proc, dir, ws: m[1] }); }
    });
    proc.on('exit', (code) => reject(new Error('Chrome exited early (' + code + ')')));
  });
}

function cdp(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let id = 0; const pending = new Map();
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pending.has(m.id)) {
      const { ok, ko } = pending.get(m.id); pending.delete(m.id);
      m.error ? ko(new Error(m.error.message)) : ok(m.result);
    }
  };
  const send = (method, params = {}, sessionId) => new Promise((ok, ko) => {
    const i = ++id; pending.set(i, { ok, ko });
    ws.send(JSON.stringify({ id: i, method, params, ...(sessionId ? { sessionId } : {}) }));
  });
  return new Promise((resolve, reject) => {
    ws.onopen = () => resolve({ send, close: () => ws.close() });
    ws.onerror = () => reject(new Error('CDP connection failed'));
  });
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  const qs = new URLSearchParams();
  if (opt('--only')) qs.set('only', opt('--only'));
  if (opt('--src')) {
    const rel = path.relative(ROOT, path.resolve(opt('--src')));
    if (rel.startsWith('..')) throw new Error('--src must be inside the project directory');
    qs.set('src', rel.split(path.sep).join('/'));
  }
  if (flag('--clicks')) qs.set('clicks', '1');

  const srv = await serve();
  const url = `http://127.0.0.1:${srv.address().port}/verify-runtime.html?${qs}`;
  const chrome = await launch(findChrome());
  let client;
  try {
    client = await cdp(chrome.ws);
    const { targetId } = await client.send('Target.createTarget', { url: 'about:blank' });
    const { sessionId } = await client.send('Target.attachToTarget', { targetId, flatten: true });
    const ev = async (expr) => (await client.send('Runtime.evaluate', { expression: expr, returnByValue: true }, sessionId)).result.value;
    await client.send('Page.enable', {}, sessionId);
    await client.send('Page.navigate', { url }, sessionId);
    const t0 = Date.now(); let last = '';
    for (;;) {
      await sleep(1000);
      const title = await ev('document.title').catch(() => '');
      if (/^(DONE|LOAD-ERROR)/.test(title)) break;
      const prog = await ev("(document.getElementById('out')||{}).textContent||''").catch(() => '');
      if (prog !== last && process.stderr.isTTY) { process.stderr.write('\r' + prog.slice(0, 60) + '   '); last = prog; }
      if (Date.now() - t0 > TIMEOUT) throw new Error('timed out after ' + TIMEOUT / 1000 + 's — ' + prog);
    }
    if (process.stderr.isTTY) process.stderr.write('\r' + ' '.repeat(70) + '\r');
    const title = await ev('document.title');
    if (title.startsWith('LOAD-ERROR')) throw new Error(await ev("document.getElementById('out').textContent"));
    const res = JSON.parse(await ev('JSON.stringify(window.__VERIFY__)'));
    report(res);
  } finally {
    try { client && client.close(); } catch {}
    chrome.proc.kill('SIGKILL');
    srv.close();
    setTimeout(() => { try { fs.rmSync(chrome.dir, { recursive: true, force: true }); } catch {} }, 300);
  }
}

function report(res) {
  const s = res.summary;
  if (flag('--json')) { console.log(JSON.stringify(res, null, 1)); }
  else {
    const L = (n, label) => console.log(`${n ? '✗' : '✓'} ${label}: ${n}`);
    console.log(`${s.total} components mounted (${s.fullSpan} full-span, ${s.webglComponents} WebGL) — clock: ${s.rafMode}`);
    L(s.errors, 'errors at mount'); L(s.asyncErrors, 'errors after mount'); L(s.blank, 'blank renders');
    if ('deadControls' in s) L(s.deadControls, `dead controls (of ${s.controlsTested} clicked)`);
    L(s.linkAndFormProblems, 'components with placeholder links or reloading forms');
    console.log(`· canvases drawing nothing: ${s.darkCanvas}   · overflowing their width: ${s.overflowing}`);
    for (const [t, a] of [['ERRORS AT MOUNT', s.errorList], ['ERRORS AFTER MOUNT', s.asyncErrorList],
      ['DEAD CONTROLS', s.deadList],
      ['UNCONFIRMED — dead only in a state other clicks created (check, not counted)', s.unconfirmedList],
      ['LINKS AND FORMS', s.findingList], ['BLANK', s.blankList],
      ['DARK CANVAS (check: may only draw on interaction)', s.darkList], ['OVERFLOWING', s.overflowList]]) {
      if (a && a.length) { console.log('\n' + t); a.forEach((x) => console.log('  ' + x)); }
    }
  }
  const fail = s.errors + s.asyncErrors + s.blank + (s.deadControls || 0) + s.linkAndFormProblems;
  console.log(fail ? `\nFAIL — ${fail} problem(s)` : '\nPASS');
  process.exitCode = fail ? 1 : 0;
}

main().catch((e) => { console.error('verify.mjs: ' + e.message); process.exitCode = 2; });

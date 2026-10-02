# Web Components Style

A self-contained library of UI design languages and copy-paste components.
No build step, no dependencies, no framework. Open the HTML files directly.

| Page | What it is |
|---|---|
| **`library.html`** | **968 components** across 103 categories, each with its own copyable source |
| **`database.html`** | **580 design languages** applied to a live 60-component interface |
| **`extreme.html`** | 21 motion studies and 44 interactive components, hand-written canvas and WebGL |
| **`scroll-lab.html`** | 9 scroll-driven animation techniques with their source alongside |
| **`index.html`** | The earlier design atlas — superseded by `database.html` |

## Run it

Everything works from `file://`, but a local server avoids browser restrictions:

```sh
python3 -m http.server 8756
```

Then open <http://localhost:8756/library.html>.

## The component library

Every component is stored as `{id, html, css, js}` and the preview is **mounted from those
exact strings** — so the code you copy can never drift from what you see.

Each one is:

- **Scoped** — every class and `@keyframes` name is prefixed with the component id, so pasting
  one into your project cannot leak styles into anything else
- **Self-contained** — no CDN, libraries, imports, web fonts or images
- **Capability-free** — no network, storage, `eval`, cookies or navigation; checked mechanically
- **Copyable four ways** — *Copy for AI*, *Copy all*, or HTML / CSS / JS separately

*Copy for AI* wraps a component with instructions, ready to paste into another AI session to
show it exactly the style you want. There is also *Copy category* and *Copy whole library*.

### Coverage

- **Motion — 200** across 17 categories: cards, charts, backgrounds, cursors, micro-interactions,
  physics, morphing, 3D, feedback, navigation, data, ambient, plus buttons, loaders, reveals,
  text and transitions
- **Finance & trading — 193**: order entry, depth and order books, price displays, trade charts,
  positions, blotters, market data, risk, portfolio, banking, payments, crypto
- **Trading desk — 64** across 8 institutional desks: hedge fund (NAV, AUM, exposure, drawdown
  vs high-water mark, LP capital accounts, fee accrual), execution (algo wheel, parent/child
  fills, VWAP vs arrival, venue routing, slippage), research, macro, derivatives (chain, greeks,
  vol smile, term structure, payoff), fixed income (yield solver, DV01, duration, spreads),
  compliance (surveillance, restricted list, audit trail) and prime brokerage (margin, stock
  loan, haircuts, settlement fails)
- **Trading charts — 48** across 6 categories: candles (OHLC, hollow, Heikin-Ashi, point &
  figure), depth, technical indicators computed live from a price series (RSI, MACD, Bollinger,
  stochastic, ATR, Ichimoku), volume profile and VWAP, performance and drawdown, correlation
- **Terminal — 151** across 18 categories: Bloomberg and Bloomberg Pro (DES, GP, PORT, ANR, ECO,
  MSG, HP), terminal charts drawn in block glyphs, quant, ticker tape and wire, keyboard command
  lines, feed and infrastructure monitors, plus CRT, TUI, DOS, System, Text, Mainframe, Retro8,
  Hacker and Modern
- **Scroll — 96** across 8 categories: reveals, parallax, sticky, progress, snap, horizontal,
  text and timelines — each building its own scroll container, so it drops into any layout
- **Modern — 80** across 10 categories: bento grids, glass, command palettes, AI chat,
  onboarding, pricing, auth, settings, empty states, toolbars
- **Interface — 112**: buttons, inputs, selection, menus, overlays, cards, data display,
  charts, feedback, marketing, media, dashboard, experimental
- **Music — 24**: players, visualisers and controls

Every component is verified twice before it ships: `libcheck.py` proves it satisfies the
contract, and `verify-runtime.html` mounts all 968 and confirms none throws or renders blank.

## The design database

580 design languages — from Swiss International and Bauhaus to Linear, Vercel, Nord, Dracula
and Windows 95. Each is **28 visual tokens plus 7 structural traits**, expanded to ~48 CSS
custom properties at runtime.

The structural traits are what make designs differ in *shape* rather than just colour:

| Trait | Options |
|---|---|
| `density` | compact · cozy · airy |
| `scale` | tight · normal · dramatic |
| `surface` | flat · outlined · raised · inset · glass |
| `input` | box · underline · filled · pill · sharp |
| `btn` | solid · outline · ghost · gradient · hard · soft |
| `divider` | hairline · heavy · dashed · none · double |
| `align` | left · center |

Pick a design and the whole 60-component kit redraws in it. Filter, compare two side by side,
check WCAG contrast, fork one in the editor and save your own, or export as CSS, SCSS,
Tailwind config or JSON.

## Building

Components live in **`components-src/`** — one JSON array per category, built in filename
order. That folder is the source of truth; `components.js` and `library.html` are generated
from it, so a fresh clone can always rebuild the library.

```sh
python3 build-lib.py # components-src/ → components.js and library.html
./build-db.sh        # rebuilds database.html and index.html from the _-prefixed partials
```

To add components, write a JSON array of them and install it. `libcheck.py` validates the
batch and writes the destination file only if every component passes:

```sh
python3 libcheck.py mybatch.json --install components-src/2000-my-category.json
python3 build-lib.py
```

A component that takes a whole row — a dashboard, an app shell, a page section — sets
`"span": "full"`.

### What is checked

`build-lib.py` validates everything through `libcheck.py` and rejects, with the reason
printed, anything that fails:

- **Scoping** — every selector must mention the component's class, or be nested inside a rule
  that does. CSS is walked with a brace stack the way a browser parses it, so minified
  rules, native CSS nesting, `@container` and `@starting-style` are all checked correctly.
- **Global names** — `@keyframes` and `@property` registrations are document-wide, so a
  name used by two components is rejected.
- **Capabilities** — no network, storage, `eval`, cookies, navigation, nested scripts or
  frames, external resources or web fonts.
- **Syntax** — every component's JS is parsed by Node.

New batches must also pass stricter rules the older library predates: `@keyframes`,
`@property` and `view-transition-name` prefixed with the id; animation loops that stop
themselves once unmounted; WebGL contexts released on unmount (browsers keep about 16);
window/document listeners removed; no `position: fixed`, viewport units or top-layer APIs
(they escape the component — container queries and `cqi` units instead); full-row components
must respond to their container; and no string shaped like a real API key, since secret
scanners would block anyone who copies the component.

Open `verify-runtime.html` to mount every component and report errors thrown at mount and
**after** mount (inside timers and animation frames, attributed to the component that threw),
blank renders, 2D and WebGL canvases that draw nothing, and components overflowing their
width. Full-row components are measured at full width. In an embedded view that freezes
`requestAnimationFrame` it substitutes a timer-driven clock.

In the library, a component's CSS is injected the first time it scrolls into view, and its
script is tagged with a `sourceURL`, so DevTools and error stacks show `components/<id>.js`.

## Notes

Brand and editor palettes reproduce published values for study and comparison. They are not
affiliated with or endorsed by their owners.

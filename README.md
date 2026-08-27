# Web Components Style

A self-contained library of UI design languages and copy-paste components.
No build step, no dependencies, no framework. Open the HTML files directly.

| Page | What it is |
|---|---|
| **`library.html`** | **472 components** across 53 categories, each with its own copyable source |
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

- **Finance & trading — 193**: order entry, depth and order books, price displays, trade charts,
  positions, blotters, market data, risk, portfolio, banking, payments, crypto
- **Terminal — 103** across 12 traditions: Bloomberg, CRT, TUI, DOS, Modern, System, Trading,
  Text, Mainframe, Retro8, Hacker
- **Music & motion — 64**: players, visualisers, controls, plus motion buttons, loaders,
  reveals, text and transitions
- **General UI — 112**: buttons, inputs, selection, menus, overlays, cards, data display,
  charts, feedback, marketing, media, dashboard, experimental

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

Source lives in the `_`-prefixed partials; the pages are generated from them.

```sh
./build-db.sh        # rebuilds database.html and index.html
python3 build-lib.py # rebuilds components.js and library.html
```

`build-lib.py` validates every component before it ships and rejects anything that fails:
unscoped selectors, colliding `@keyframes`, JS syntax errors, disallowed capabilities, or a
proven runtime failure. Rejections are printed with their reason rather than shipped broken.

## Notes

Brand and editor palettes reproduce published values for study and comparison. They are not
affiliated with or endorsed by their owners.

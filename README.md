# Web Components Style

A self-contained library of UI design languages and copy-paste components.
No build step, no dependencies, no framework. Open the HTML files directly.

| Page | What it is |
|---|---|
| **`library.html`** | **1608 components** across 183 categories, each with its own copyable source |
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

- **App templates — 192** across 24 kinds, each a full-row, fully interactive app shell: Admin & CMS, Auth Pages, Booking & Events, Calendar, Chat, Creative Tools, Developer Tools, Editor, Files, Fitness & Habits, HR & People, Kanban, Learning, Mail, Media, Mobility & Delivery, Notes & Tasks, Personal Finance, Point of Sale, Real Estate, Restaurant, Smart Home, Storefront, Travel
- **Dashboards — 208** across 26 business domains: AI Ops, Agency, Analytics, Commerce, Customer Support, DevOps, Education, Executive, Field Service, Fintech, Gaming, HR & Workforce, Health, Hospitality, Insurance, IoT & Energy, Legal Ops, Logistics, Marketing, Media & Publishing, Nonprofit, Projects, Real Estate, Retail Stores, SaaS, Sales CRM
- **Page blocks — 80**: CTA, FAQ & Contact, Features, Footer, Hero, Navbar, Pricing, Showcase, Stats & Logos, Testimonials — full-row landing-page sections
- **FX — 80**: Data Art, Generative, Glow & Light, Hover, Liquid & Glass, Particles, Shaders, Spatial, Text, View Transitions — WebGL shaders, particle systems, liquid glass, view transitions and more
- **Modern UI — 160**: AI Chat, Auth, Bento, Command, Commerce, Data Grid, Date & Time, Drag & Drop, Empty, Forms, Glass, Media, Navigation, Notifications, Onboarding, Pricing, Settings, Social, Toolbars, Uploads
- **Motion — 200** across 17 categories: 3D, Ambient, Backgrounds, Buttons, Cards, Charts, Cursors, Data, Feedback, Loaders, Micro, Morph, Navigation, Physics, Reveals, Text, Transitions
- **Scroll — 96**: Horizontal, Parallax, Progress, Reveals, Snap, Sticky, Text, Timeline — each building its own scroll container, so it drops into any layout
- **Finance & trading — 193**: order entry, depth and order books, price displays, trade charts,
  positions, blotters, market data, risk, portfolio, banking, payments, crypto
- **Trading desk — 64** across 8 institutional desks: Compliance, Derivatives, Execution, Fixed Income, Hedge Fund, Macro, Prime Brokerage, Research
- **Trading charts — 48**: Candles, Correlation, Depth, Performance, Technical, Volume — indicators computed live from a price series
- **Terminal — 151** across 18 categories, from Bloomberg and Bloomberg Pro to CRT, TUI, DOS and quant
- **Interface — 112**: buttons, inputs, selection, menus, overlays, cards, data display, charts,
  feedback, marketing, media, dashboard, experimental
- **Music — 24**: players, visualisers and controls

Every interactive component in the App, Dashboard and newer families passed a headless click
check that clicks every control and fails any that does nothing.

Every component is verified twice before it ships: `libcheck.py` proves it satisfies the
contract, and `verify-runtime.html` mounts all 1608 and confirms none throws or renders blank.

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

### Runtime and click checking

`tools/verify.mjs` runs the runtime checks in headless Chrome from the command line — no
dependencies beyond Node 22+ and an installed Chrome:

```sh
node tools/verify.mjs                                   # every component in components.js
node tools/verify.mjs --only dba-,apm-                  # ids starting with these prefixes
node tools/verify.mjs --src components-src/1210-app-mail.json --clicks
```

`--clicks` clicks every button, link, tab, menu item, option, switch, row and anything styled
as clickable, on a freshly mounted copy, and fails any control that changes nothing. It clicks
what a real pointer would hit, scrolls hidden controls into view first, re-tests suspected
dead controls on a fresh mount, and does not count options that are already selected, fields
operated by dragging or typing, drag handles, or file pickers (opening one counts as an
action). It also reports `href="#"` placeholder links and forms that would reload the page.
It exits non-zero on any error, blank render, dead control or placeholder link.

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

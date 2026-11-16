# Education drivers knowledge graph

This repository contains a curated, source-linked education drivers graph and a
read-only React Flow viewer. The app lets visitors pan and zoom the map and
select nodes or relationships to inspect their details. It does not currently
let visitors edit the graph or submit changes.

## Run the viewer locally

Requires Python 3, Node.js and npm:

```sh
npm ci
npm run dev
```

Open the local URL printed by Vite. `npm run build` regenerates the graph data
and builds the static site in `dist/`; `npm run preview` serves that build. To
check the data exporter, run `python3 -m unittest`.

## Where to make changes

| What you want to change | Start here |
| --- | --- |
| Page title, heading, or introductory text | `index.html` (browser-tab title), `src/App.jsx` (page heading and graph area), `src/Sidebar.jsx` (instructions and notices) |
| Colours, typography, spacing, responsive layout, node sizes, selection and edge appearance | `src/styles.css` |
| Node shape and the way its label is drawn | `src/CustomNode.jsx`; shape geometry comes from `export_graph.py` |
| What a node or relationship shows when selected | `src/Sidebar.jsx`; selection and graph event handling are in `src/App.jsx` |
| Node and relationship data, including labels, colours, shapes, references, and notes | `nodes.csv` and `relationships.csv` |
| Automatic graph spacing and arrangement | `src/layout.js` |
| Which graph files load and how edges are styled | `src/App.jsx` |

### Change the look

Most visual changes belong in `src/styles.css`. It controls the page layout,
sidebar, typography, graph nodes, node selection, relationship lines, and the
small-screen layout. For example, edit `.header` or `.sidebar` for the page
panels, `.graph-node` or `.node-shape` for node size and labels, and the
`.shape-*` rules for shape-specific label spacing. The `@media` rule adjusts the
layout on narrow screens.

Node fill colours and shapes are data-driven: edit the `colour` and `shape`
values in `nodes.csv`. Supported shape names are `square`, `diamond`,
`pentagon`, `hexagon`, `septagon`, `triangle`, and `circle`. The corresponding
shape geometry is defined in `export_graph.py` (`SHAPES`). Relationship colours
come from the `colour` column in `relationships.csv`; when it is empty, the app
uses its default edge colour in `src/App.jsx`.

To change the node markup or label rendering, edit `src/CustomNode.jsx`. To
change the detail panel's content or field order, edit `src/Sidebar.jsx`. The
selected item's data is passed to the sidebar from `src/App.jsx`.

### Change the graph layout or behavior

`src/layout.js` uses a deterministic d3-force simulation to calculate initial
node positions. Adjust the link distance and strength, charge, collision radius,
X/Y force strengths, or number of simulation ticks there to change the overall
spacing. These are starting positions; users can still pan and zoom in the
viewer.

`src/App.jsx` wires together the graph, loading/error states, selection, and
read-only settings. For example, node and edge click handlers control what is
selected, and `nodesDraggable={false}` keeps nodes fixed. This is the place to
change graph interactions or add controls such as search and filters. The
current app is intentionally read-only; enabling drag or adding controls to
edit data would also require deciding how those changes are saved.

### Change the graph content

For ordinary content changes, edit the CSV files:

- `nodes.csv` has `id`, `name`, `level`, `category`, `description`, `colour`,
  and `shape` columns.
- `relationships.csv` has `id`, `source`, `target`, `type`, `references`,
  `direction`, `confidence`, `symbol`, `notes`, `reviewed_by`, `last_updated`,
  `colour`, and `evidence_basis` columns.

Keep IDs unique and make sure every relationship's `source` and `target` match
an existing node ID. The exporter checks these constraints and rejects unknown
shapes. After changing the CSVs, regenerate the JSON consumed by the app:

```sh
npm run data
```

Then use `npm run dev` to review the result or `npm run build` to generate the
production site. `export_graph.py` reads the CSVs and writes `nodes.json`,
`edges.json`, and `styles.json` to `public/data/`. Treat those JSON files as
generated output rather than the place to make source edits.

`build_graph.py` is the workbook-to-CSV curation pipeline. It requires
`openpyxl` and the original source workbook; see `validation.txt` for workbook
regeneration, validation, and interpretation limitations. If you regenerate
the CSVs from the workbook, run `npm run data` afterward to refresh the app's
JSON files.

## Interpreting the graph

The references are the menu's citations and have not been independently
checked against full-text studies. A supports relationship describes a
menu-reported component, intended contribution, mechanism or finding, not
necessarily a causal effect. Indicator relationships describe measures, not
evidence of observed change. Confidence ratings and notation are blank where
the source does not support assigning them; the viewer does not infer them.
See `validation.txt` for further limitations.

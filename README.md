# Education drivers knowledge graph

This repository contains a curated, source-linked education drivers graph and a
read-only React Flow viewer. Select a node or relationship to see its context.
The map can be panned and zoomed, but nodes and relationships cannot be edited.
Public submissions are not enabled.

## Run the viewer

Requires Python 3, Node.js and npm:

```sh
npm ci
npm run data
npm run dev
```

Open the local URL printed by Vite. `npm run build` regenerates the data and
builds the static site in `dist/`; `npm run preview` serves that build.

`export_graph.py` reads `nodes.csv` and `relationships.csv` and writes React Flow
`nodes.json`, `edges.json` and shape CSS `styles.json` to `public/data/`.
Use `--input-dir` and `--output-dir` to override those directories. The viewer
positions the graph with a deterministic d3-force simulation on load; positions
in the exported JSON are placeholders. Run `python3 -m unittest` to check the
exporter.

The original `build_graph.py` remains the workbook-to-CSV curation pipeline.
It requires `openpyxl` and the original source workbook; see `validation.txt`
for regeneration and validation details. Run the JSON export again after
changing the CSVs.

## Interpreting the graph

The references are the menu's citations and have not been independently
checked against full-text studies. A supports relationship describes a
menu-reported component, intended contribution, mechanism or finding, not
necessarily a causal effect. Indicator relationships describe measures, not
evidence of observed change. Confidence ratings and notation are blank where
the source does not support assigning them; the viewer does not infer them.
See `validation.txt` for further limitations.

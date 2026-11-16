#!/usr/bin/env python3
"""Export the curated CSV graph as React Flow data."""

import argparse
import csv
import json
from pathlib import Path


SHAPES = {
    "square": {},
    "diamond": {"clipPath": "polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)"},
    "pentagon": {"clipPath": "polygon(50% 0%, 100% 38%, 81% 100%, 19% 100%, 0% 38%)"},
    "hexagon": {"clipPath": "polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)"},
    "septagon": {"clipPath": "polygon(50% 0%, 89% 19%, 100% 61%, 72% 100%, 28% 100%, 0% 61%, 11% 19%)"},
    "triangle": {"clipPath": "polygon(50% 0%, 100% 100%, 0% 100%)"},
    "circle": {"borderRadius": "50%"},
}

NODE_FIELDS = {"id", "name", "level", "category", "description", "colour", "shape"}
EDGE_FIELDS = {
    "id", "source", "target", "type", "references", "direction", "confidence",
    "symbol", "notes", "reviewed_by", "last_updated", "colour", "evidence_basis",
}


def read_csv(path, required_fields):
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        missing = required_fields - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: missing columns: {', '.join(sorted(missing))}")
        return list(reader)


def export_graph(input_dir, output_dir):
    raw_nodes = read_csv(input_dir / "nodes.csv", NODE_FIELDS)
    raw_edges = read_csv(input_dir / "relationships.csv", EDGE_FIELDS)
    ids = set()
    nodes = []
    for row in raw_nodes:
        identifier = row["id"].strip()
        if not identifier or identifier in ids:
            raise ValueError(f"Empty or duplicate node ID: {identifier!r}")
        if row["shape"] not in SHAPES:
            raise ValueError(f"Unknown shape {row['shape']!r} for node {identifier!r}")
        ids.add(identifier)
        nodes.append({
            "id": identifier,
            "type": "custom",
            "position": {"x": 0, "y": 0},
            "data": {key: value for key, value in row.items() if key != "id"},
        })

    edges = []
    edge_ids = set()
    for row in raw_edges:
        identifier = row["id"].strip()
        if not identifier or identifier in edge_ids:
            raise ValueError(f"Empty or duplicate relationship ID: {identifier!r}")
        if row["source"] not in ids or row["target"] not in ids:
            raise ValueError(f"Unknown endpoint for relationship {identifier!r}")
        edge_ids.add(identifier)
        edges.append({
            "id": identifier,
            "source": row["source"],
            "target": row["target"],
            "data": {key: value for key, value in row.items()
                     if key not in {"id", "source", "target"}},
        })

    output_dir.mkdir(parents=True, exist_ok=True)
    for name, value in (("nodes", nodes), ("edges", edges), ("styles", SHAPES)):
        (output_dir / f"{name}.json").write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "public" / "data")
    args = parser.parse_args()
    export_graph(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()

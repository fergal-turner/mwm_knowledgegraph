import csv
import json
import tempfile
import unittest
from pathlib import Path

from export_graph import EDGE_FIELDS, NODE_FIELDS, SHAPES, export_graph


class ExportGraphTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.nodes = [
            dict.fromkeys(NODE_FIELDS, "") | {
                "id": "a", "name": "First", "shape": "hexagon", "colour": "#007f79",
                "description": "Context",
            },
            dict.fromkeys(NODE_FIELDS, "") | {"id": "b", "name": "Second", "shape": "circle"},
        ]
        self.edges = [
            dict.fromkeys(EDGE_FIELDS, "") | {
                "id": "a_b", "source": "a", "target": "b", "symbol": "+++",
                "notes": "Evidence", "references": "Source",
            }
        ]

    def write_csvs(self):
        for name, fields, rows in (
            ("nodes.csv", NODE_FIELDS, self.nodes),
            ("relationships.csv", EDGE_FIELDS, self.edges),
        ):
            with (self.root / name).open("w", encoding="utf-8-sig", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=sorted(fields))
                writer.writeheader()
                writer.writerows(rows)

    def test_exports_react_flow_data_and_styles(self):
        self.write_csvs()
        output = self.root / "output"
        export_graph(self.root, output)
        nodes = json.loads((output / "nodes.json").read_text())
        edges = json.loads((output / "edges.json").read_text())
        styles = json.loads((output / "styles.json").read_text())
        self.assertEqual(nodes[0]["data"]["description"], "Context")
        self.assertEqual(nodes[0]["type"], "custom")
        self.assertEqual(edges[0]["data"]["symbol"], "+++")
        self.assertEqual(edges[0]["data"]["references"], "Source")
        self.assertEqual(styles, SHAPES)
        self.assertEqual(styles["circle"], {"borderRadius": "50%"})
        self.assertIn("clipPath", styles["hexagon"])

    def test_rejects_bad_endpoints_and_shapes(self):
        self.edges[0]["target"] = "missing"
        self.write_csvs()
        with self.assertRaisesRegex(ValueError, "Unknown endpoint"):
            export_graph(self.root, self.root / "output")
        self.edges[0]["target"] = "b"
        self.nodes[0]["shape"] = "unknown"
        self.write_csvs()
        with self.assertRaisesRegex(ValueError, "Unknown shape"):
            export_graph(self.root, self.root / "output")

    def test_rejects_duplicate_ids_and_missing_columns(self):
        self.nodes[1]["id"] = "a"
        self.write_csvs()
        with self.assertRaisesRegex(ValueError, "duplicate node ID"):
            export_graph(self.root, self.root / "output")
        (self.root / "nodes.csv").write_text("id,name\na,First\n")
        with self.assertRaisesRegex(ValueError, "missing columns"):
            export_graph(self.root, self.root / "output")


if __name__ == "__main__":
    unittest.main()

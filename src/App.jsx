import { useEffect, useState } from 'react';
import { Background, Controls, MarkerType, ReactFlow } from '@xyflow/react';
import CustomNode from './CustomNode.jsx';
import Sidebar from './Sidebar.jsx';
import { layoutGraph } from './layout.js';

const nodeTypes = { custom: CustomNode };

async function loadJson(name, signal) {
  const response = await fetch(`${import.meta.env.BASE_URL}data/${name}.json`, { signal });
  if (!response.ok) throw new Error(`Could not load ${name}.json (${response.status})`);
  return response.json();
}

export default function App() {
  const [graph, setGraph] = useState(null);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    Promise.all(['nodes', 'edges', 'styles'].map((name) => loadJson(name, controller.signal)))
      .then(([nodes, edges, styles]) => {
        const styledNodes = nodes.map((node) => ({
          ...node,
          data: { ...node.data, shapeStyle: styles[node.data.shape] },
        }));
        const names = Object.fromEntries(nodes.map((node) => [node.id, node.data.name]));
        setGraph({
          nodes: layoutGraph(styledNodes, edges),
          edges: edges.map((edge) => ({
            ...edge,
            label: edge.data.symbol || undefined,
            style: { stroke: edge.data.colour || '#718096' },
            markerEnd: { type: MarkerType.ArrowClosed, color: edge.data.colour || '#718096' },
          })),
          names,
        });
      })
      .catch((reason) => {
        if (reason.name !== 'AbortError') setError(reason.message);
      });
    return () => controller.abort();
  }, []);

  return (
    <main className="app">
      <header className="header">
        <p className="eyebrow">Source-linked education drivers</p>
        <h1>Knowledge graph</h1>
      </header>
      <div className="workspace">
        <section className="graph" aria-label="Knowledge graph">
          {error ? <p role="alert" className="status">Unable to load the graph: {error}</p> : !graph ? (
            <p className="status">Loading graph…</p>
          ) : (
            <ReactFlow
              nodes={graph.nodes.map((node) => ({
                ...node, selected: selected?.kind === 'node' && selected.id === node.id,
              }))}
              edges={graph.edges.map((edge) => ({
                ...edge, selected: selected?.kind === 'edge' && selected.id === edge.id,
              }))}
              nodeTypes={nodeTypes}
              nodesDraggable={false}
              nodesConnectable={false}
              elementsSelectable
              onNodeClick={(_, node) => setSelected({ kind: 'node', id: node.id, data: node.data })}
              onEdgeClick={(_, edge) => setSelected({
                kind: 'edge', id: edge.id, data: edge.data,
                sourceName: graph.names[edge.source], targetName: graph.names[edge.target],
              })}
              onPaneClick={() => setSelected(null)}
              fitView
              minZoom={0.02}
              fitViewOptions={{ padding: 0.1 }}
            >
              <Background />
              <Controls showInteractive={false} />
            </ReactFlow>
          )}
        </section>
        <Sidebar selected={selected} />
      </div>
    </main>
  );
}

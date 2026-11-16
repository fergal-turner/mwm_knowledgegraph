import { useEffect, useState, useRef } from 'react';
import { Background, Controls, MarkerType, ReactFlow } from '@xyflow/react';
import CustomNode from './CustomNode.jsx';
import Sidebar from './Sidebar.jsx';
import Legend from './Legend.jsx';
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
  const [expanded, setExpanded] = useState(new Set());
  const [error, setError] = useState('');
  const positionCacheRef = useRef(new Map());

  useEffect(() => {
    const controller = new AbortController();
    Promise.all(['nodes', 'edges', 'styles'].map((name) => loadJson(name, controller.signal)))
      .then(([nodes, edges, styles]) => {
        const styledNodes = nodes.map((node) => ({
          ...node,
          data: { ...node.data, shapeStyle: styles[node.data.shape] },
        }));
        const names = Object.fromEntries(nodes.map((node) => [node.id, node.data.name]));
        
        // Layout all nodes initially and cache positions
        const layoutedNodes = layoutGraph(styledNodes, edges);
        layoutedNodes.forEach((node) => {
          positionCacheRef.current.set(node.id, node.position);
        });

        setGraph({
          allNodes: styledNodes,
          allEdges: edges,
          names,
        });
      })
      .catch((reason) => {
        if (reason.name !== 'AbortError') setError(reason.message);
      });
    return () => controller.abort();
  }, []);

  function getVisibleElements() {
    if (!graph) return { nodes: [], edges: [] };

    // Default: only show outcomes and results
    if (!selected || selected.kind === 'edge') {
      const visibleNodeIds = new Set(
        graph.allNodes
          .filter((n) => n.data.category === 'outcome' || n.data.category === 'result')
          .map((n) => n.id)
      );
      const visibleNodes = graph.allNodes.filter((n) => visibleNodeIds.has(n.id));
      const visibleEdges = graph.allEdges.filter(
        (e) => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target)
      );
      return { nodes: visibleNodes, edges: visibleEdges };
    }

    // When a node is selected: show it + direct connections only
    let visibleNodeIds = new Set([selected.id]);

    // Add direct parents (edges where target === selected node)
    graph.allEdges.forEach((edge) => {
      if (edge.target === selected.id) {
        visibleNodeIds.add(edge.source);
      }
    });

    // Add direct children (edges where source === selected node)
    graph.allEdges.forEach((edge) => {
      if (edge.source === selected.id) {
        visibleNodeIds.add(edge.target);
      }
    });

    // Filter nodes and edges
    const visibleNodes = graph.allNodes.filter((n) => visibleNodeIds.has(n.id));
    const visibleEdges = graph.allEdges.filter(
      (e) => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target)
    );

    return { nodes: visibleNodes, edges: visibleEdges };
  }

  const { nodes: visibleNodes, edges: visibleEdges } = getVisibleElements();

  // Use cached positions, layout only new nodes
  const displayNodes = visibleNodes.map((node) => {
    const cachedPos = positionCacheRef.current.get(node.id);
    return {
      ...node,
      type: 'custom',
      selected: selected?.id === node.id,
      position: cachedPos || { x: 0, y: 0 },
      data: { ...node.data, isExpanded: expanded.has(node.id) },
    };
  });

  const displayEdges = visibleEdges.map((edge) => {
    const color = edge.data?.colour || '#a0aec0';
    return {
      ...edge,
      id: edge.id || `${edge.source}-${edge.target}`,
      type: 'straight',
      label: edge.data.symbol || undefined,
      style: { 
        stroke: color,
        filter: 'drop-shadow(0 0 4px rgba(100,150,200,0.4))',
      },
      markerEnd: { type: MarkerType.ArrowClosed, color },
    };
  });

  function handleNodeClick(node) {
    console.log('Node clicked:', node.id, node.data.name);
    
    if (selected?.id === node.id) {
      // Click again to deselect
      setSelected(null);
    } else {
      // Select the node
      setSelected({ kind: 'node', id: node.id, data: node.data });
    }
  }

  const handleReset = () => {
    setSelected(null);
    setExpanded(new Set());
  };

  return (
    <main className="app">
      <header className="header">
        <div className="header-content">
            <div>
              <p className="eyebrow">Source-linked education drivers</p>
              <h1>Knowledge graph</h1>
            </div>
            <img src="public/data/logo.svg" alt="Logo" style={{height: '60px'}} />
          </div>
      </header>
      <div className="workspace">
        <section className="graph" aria-label="Source-Linked Driver Map">
          {error ? (
            <p role="alert" className="status">Unable to load the graph: {error}</p>
          ) : !graph ? (
            <p className="status">Loading graph…</p>
          ) : (
            <ReactFlow
              nodes={displayNodes}
              edges={displayEdges}
              nodeTypes={nodeTypes}
              nodesDraggable={true}
              nodesConnectable={false}
              elementsSelectable
              onNodeClick={(_, node) => handleNodeClick(node)}
              onEdgeClick={(_, edge) => {
                setSelected({
                  kind: 'edge',
                  id: edge.id,
                  data: edge.data,
                  sourceName: graph.names[edge.source],
                  targetName: graph.names[edge.target],
                });
              }}
              onPaneClick={() => setSelected(null)}
              fitView
              minZoom={0.02}
              fitViewOptions={{ padding: 0.1 }}
            >
              <Background variant="cross" gap={50} size={1} />
              <Controls showInteractive={false} />
              <Legend />
            </ReactFlow>
          )}
        </section>
        <Sidebar selected={selected} />
      </div>
    </main>
  );
}

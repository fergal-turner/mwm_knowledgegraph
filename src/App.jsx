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
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);
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
    if (!selectedNode) {
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

    const selectedCategory = selectedNode.data.category;
    let visibleNodeIds = new Set([selectedNode.id]);

    if (selectedCategory === 'outcome') {
      // Outcome selected: show only direct results connected to it
      graph.allEdges.forEach((edge) => {
        if (edge.target === selectedNode.id) {
          // Direct children: edges where target is outcome, source is result
          visibleNodeIds.add(edge.source);
        }
      });
    } else if (selectedCategory === 'result') {
      // Result selected: show result + outcomes (parents via source) + drivers (children via target)
      graph.allEdges.forEach((edge) => {
        if (edge.source === selectedNode.id) {
          // Parents (outcomes) - follow edge source upward
          visibleNodeIds.add(edge.target);
        }
        if (edge.target === selectedNode.id) {
          // Children (drivers) - follow edge target downward
          visibleNodeIds.add(edge.source);
        }
      });
    } else {
      // Driver/Activity/Measurement: show selected node + direct children + complete parent chain to outcome
      
      // Add direct children (edges where current node is target, source is child)
      graph.allEdges.forEach((edge) => {
        if (edge.target === selectedNode.id) {
          visibleNodeIds.add(edge.source);
        }
      });

      // Trace parent chain up to outcome (follow source → target upward)
      let currentNodes = [selectedNode.id];
      const visited = new Set([selectedNode.id]);

      while (currentNodes.length > 0) {
        const nextNodes = [];
        currentNodes.forEach((id) => {
          graph.allEdges.forEach((edge) => {
            // Find parents (edges where source === current node, target is parent)
            if (edge.source === id && !visited.has(edge.target)) {
              visibleNodeIds.add(edge.target);
              visited.add(edge.target);
              nextNodes.push(edge.target);
            }
          });
        });
        currentNodes = nextNodes;
      }
    }

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
      selected: selectedNode?.id === node.id,
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
      style: { 
        stroke: color,
        filter: 'drop-shadow(0 0 4px rgba(100,150,200,0.4))',
      },
      selected: selectedEdge?.id === edge.id,
    };
  });

  function handleNodeClick(node) {
    console.log('Node clicked:', node.id, node.data.name);
    
    if (selectedNode?.id === node.id) {
      // Click again to deselect
      setSelectedNode(null);
    } else {
      // Select the node
      setSelectedNode({ kind: 'node', id: node.id, data: node.data });
      setSelectedEdge(null); // Clear edge selection when selecting different node
    }
  }

  const handleEdgeClick = (_, edge) => {
    if (selectedEdge?.id === edge.id) {
      setSelectedEdge(null);
    } else {
      // Keep selectedNode active for map visibility, only update edge selection for sidebar
      setSelectedEdge({
        kind: 'edge',
        id: edge.id,
        data: edge.data,
        sourceName: graph.names[edge.source],
        targetName: graph.names[edge.target],
      });
    }
  };

  const handleReset = () => {
    setSelectedNode(null);
    setSelectedEdge(null);
    setExpanded(new Set());
  };

  return (
    <main className="app">
      <header className="header">
        <div className="header-content">
            <div>
              <p className="eyebrow">Measuring what Matters</p>
              <h1>Knowledge Graph of Evidence Based Drivers of Learning in Crisis</h1>
            </div>
            <img src={`${import.meta.env.BASE_URL}logo.svg`} alt="Logo" style={{height: '60px'}} />
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
              onEdgeClick={handleEdgeClick}
              onPaneClick={() => {
                setSelectedNode(null);
                setSelectedEdge(null);
              }}
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
        <Sidebar selectedNode={selectedNode} selectedEdge={selectedEdge} />
      </div>
    </main>
  );
}

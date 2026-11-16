import { forceCollide, forceLink, forceManyBody, forceSimulation, forceX, forceY } from 'd3-force';

export function layoutGraph(nodes, edges) {
  const points = nodes.map((node) => ({ id: node.id }));
  const links = edges.map(({ source, target }) => ({ source, target }));
  const simulation = forceSimulation(points)
    .force('link', forceLink(links).id((node) => node.id).distance(230).strength(0.35))
    .force('charge', forceManyBody().strength(-250))
    .force('collision', forceCollide(115).iterations(2))
    .force('x', forceX().strength(0.015))
    .force('y', forceY().strength(0.015))
    .stop();

  simulation.tick(350);
  return nodes.map((node, index) => ({
    ...node,
    position: { x: points[index].x, y: points[index].y },
  }));
}

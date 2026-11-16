import { forceCollide, forceLink, forceManyBody, forceSimulation, forceX, forceY } from 'd3-force';

export function layoutGraph(nodes, edges) {
  if (nodes.length === 0) return [];

  const categoryLevels = {
    outcome: 0,
    result: 1,
    driver: 2,
    activity: 3,
  };

  const points = nodes.map((node) => ({
    id: node.id,
    category: node.data.category,
    level: categoryLevels[node.data.category] || 0,
  }));

  const links = edges
    .filter((e) => points.some((p) => p.id === e.source) && points.some((p) => p.id === e.target))
    .map(({ source, target }) => ({ source, target }));

  // Initialize positions based on level
  const levelX = { 0: -400, 1: -400, 2: 0, 3: 400 };
  const levelCounts = { 0: 0, 1: 0, 2: 0, 3: 0 };

  points.forEach((point) => {
    const level = point.level;
    point.x = levelX[level] + (Math.random() - 0.5) * 60;
    point.y = levelCounts[level] * 100 - 300;
    levelCounts[level]++;
  });

  // Use force simulation with level-based forces
  const simulation = forceSimulation(points)
    .force('link', forceLink(links).id((d) => d.id).distance(120).strength(0.6))
    .force('charge', forceManyBody().strength(-100))
    .force('collision', forceCollide(50).iterations(1))
    // Push nodes toward their level's x-position
    .force('x', forceX()
      .strength(0.15)
      .x((d) => levelX[d.level])
    )
    // Weak vertical centering to let gravity take over
    .force('y', forceY().strength(0.08).y(0))
    .stop();

  // Run simulation
  simulation.tick(400);

  // Map positions back to nodes
  return nodes.map((node) => {
    const point = points.find((p) => p.id === node.id);
    return {
      ...node,
      position: { x: point.x, y: point.y },
    };
  });
}

import React from 'react';
import { createRoot } from 'react-dom/client';
import '@xyflow/react/dist/style.css';
import './styles.css';
import App from './App.jsx';

// Inject SVG marker definitions globally
const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
svg.setAttribute('style', 'display: none;');
svg.innerHTML = `
  <defs>
    <marker id="arrow-f0aec0" markerWidth="20" markerHeight="20" markerUnits="strokeWidth" orient="auto" refX="10" refY="10">
      <path d="M0,0 L0,20 L20,10 z" fill="#a0aec0"/>
    </marker>
    <marker id="arrow-F6B0BD" markerWidth="20" markerHeight="20" markerUnits="strokeWidth" orient="auto" refX="10" refY="10">
      <path d="M0,0 L0,20 L20,10 z" fill="#F6B0BD"/>
    </marker>
    <marker id="arrow-FFD5A5" markerWidth="20" markerHeight="20" markerUnits="strokeWidth" orient="auto" refX="10" refY="10">
      <path d="M0,0 L0,20 L20,10 z" fill="#FFD5A5"/>
    </marker>
    <marker id="arrow-C9DDED" markerWidth="20" markerHeight="20" markerUnits="strokeWidth" orient="auto" refX="10" refY="10">
      <path d="M0,0 L0,20 L20,10 z" fill="#C9DDED"/>
    </marker>
    <marker id="arrow-D1E5D9" markerWidth="20" markerHeight="20" markerUnits="strokeWidth" orient="auto" refX="10" refY="10">
      <path d="M0,0 L0,20 L20,10 z" fill="#D1E5D9"/>
    </marker>
  </defs>
`;
document.body.appendChild(svg);

createRoot(document.getElementById('root')).render(<App />);

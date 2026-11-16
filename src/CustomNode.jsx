import { Handle, Position } from '@xyflow/react';

export default function CustomNode({ data, selected }) {
  return (
    <div className="graph-node" style={{ pointerEvents: 'auto' }}>
      {/* Node dot - with handles positioned relative to it */}
      <div
        className={`node-dot shape-${data.shape} ${selected ? 'node-dot-selected' : ''}`}
        style={{ backgroundColor: data.colour, position: 'relative' }}
      >
        {/* Multiple handles at all positions */}
        <Handle type="target" position={Position.Top} isConnectable={false} />
        <Handle type="target" position={Position.Bottom} isConnectable={false} />
        <Handle type="target" position={Position.Left} isConnectable={false} />
        <Handle type="target" position={Position.Right} isConnectable={false} />
        
        <Handle type="source" position={Position.Top} isConnectable={false} />
        <Handle type="source" position={Position.Bottom} isConnectable={false} />
        <Handle type="source" position={Position.Left} isConnectable={false} />
        <Handle type="source" position={Position.Right} isConnectable={false} />
      </div>
      
      {/* Label */}
      <div className="node-label">{data.name}</div>
    </div>
  );
}

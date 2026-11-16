import { Handle, Position } from '@xyflow/react';

function textColour(background) {
  const hex = background.replace('#', '');
  if (!/^[\da-f]{6}$/i.test(hex)) return '#111827';
  const [red, green, blue] = [0, 2, 4].map((offset) => parseInt(hex.slice(offset, offset + 2), 16));
  return (red * 299 + green * 587 + blue * 114) / 1000 < 145 ? '#fff' : '#111827';
}

export default function CustomNode({ data, selected }) {
  return (
    <div className={`graph-node${selected ? ' graph-node-selected' : ''}`}>
      <Handle type="target" position={Position.Left} isConnectable={false} />
      <div
        className={`node-shape shape-${data.shape}`}
        style={{ ...data.shapeStyle, backgroundColor: data.colour, color: textColour(data.colour) }}
      >
        <span>{data.name}</span>
      </div>
      <Handle type="source" position={Position.Right} isConnectable={false} />
    </div>
  );
}

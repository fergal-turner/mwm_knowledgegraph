import { Handle, Position } from '@xyflow/react';

export default function CustomNode({ data, selected }) {
  // Convert hex to HSL, reduce saturation and slightly darken for muted appearance
  const getMutedColor = (hex) => {
    const r = parseInt(hex.slice(1, 3), 16) / 255;
    const g = parseInt(hex.slice(3, 5), 16) / 255;
    const b = parseInt(hex.slice(5, 7), 16) / 255;

    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;

    if (max === min) {
      h = s = 0;
    } else {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: h = (g - b) / d + (g < b ? 6 : 0); break;
        case g: h = (b - r) / d + 2; break;
        case b: h = (r - g) / d + 4; break;
      }
      h /= 6;
    }

    // Reduce saturation to 50% of original and darken slightly
    s = s * 0.4;
    l = l * 0.6;

    h = Math.round(h * 360);
    s = Math.round(s * 100);
    l = Math.round(l * 100);

    return `hsl(${h}, ${s}%, ${l}%)`;
  };

  const shapeSize = 24;
  const color = data.colour;
  const fillColor = getMutedColor(color);

  // SVG shape components with glow filter
  const renderShape = () => {
    const svgProps = {
      width: shapeSize,
      height: shapeSize,
      viewBox: "0 0 24 24",
      style: { position: 'relative' },
      filter: selected ? `drop-shadow(0 0 8px ${color})` : `drop-shadow(0 0 4px ${color}40)`
    };

    switch (data.shape) {
      case 'circle':
        return (
          <svg {...svgProps}>
            <circle cx="12" cy="12" r="10" fill={fillColor} stroke={color} strokeWidth="1.5" />
          </svg>
        );
      case 'triangle':
        return (
          <svg {...svgProps}>
            <polygon points="12,2 22,20 2,20" fill={fillColor} stroke={color} strokeWidth="1.5" />
          </svg>
        );
      case 'square':
        return (
          <svg {...svgProps}>
            <rect x="4" y="4" width="16" height="16" fill={fillColor} stroke={color} strokeWidth="1.5" />
          </svg>
        );
      case 'diamond':
        return (
          <svg {...svgProps}>
            <polygon points="12,2 22,12 12,22 2,12" fill={fillColor} stroke={color} strokeWidth="1.5" />
          </svg>
        );
      case 'pentagon':
        return (
          <svg {...svgProps}>
            <polygon points="12,2 22,8 18,20 6,20 2,8" fill={fillColor} stroke={color} strokeWidth="1.5" />
          </svg>
        );
      case 'hexagon':
        return (
          <svg {...svgProps}>
            <polygon points="6,2 18,2 22,12 18,22 6,22 2,12" fill={fillColor} stroke={color} strokeWidth="1.5" />
          </svg>
        );
      case 'septagon':
        return (
          <svg {...svgProps}>
            <polygon points="12,1 20,5 23,14 18,22 6,22 1,14 4,5" fill={fillColor} stroke={color} strokeWidth="1.5" />
          </svg>
        );
      default:
        return (
          <svg {...svgProps}>
            <circle cx="12" cy="12" r="10" fill={fillColor} stroke={color} strokeWidth="1.5" />
          </svg>
        );
    }
  };

  return (
    <div className="graph-node" style={{ pointerEvents: 'auto' }}>
      {/* Node dot - with handles positioned relative to it */}
      <div
        className={`node-dot ${selected ? 'node-dot-selected' : ''}`}
        style={{ 
          position: 'relative',
          width: '24px',
          height: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 150ms ease'
        }}
      >
        {renderShape()}

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

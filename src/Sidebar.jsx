function Field({ label, value }) {
  return (
    <div className="detail">
      <dt>{label}</dt>
      <dd>{value || 'Not specified'}</dd>
    </div>
  );
}

export default function Sidebar({ selectedNode, selectedEdge }) {
  const selected = selectedNode || selectedEdge;

  return (
    <aside className="sidebar" aria-label="Graph details">
      {!selected ? (
        <>
          <p className="eyebrow">Explore the evidence</p>
          <h2>Select a node or relationship</h2>
          <p>Click an item to see its context and source information. Zoom and pan to explore the map.</p>
          <p className="notice">A relationship describes a menu-reported component, mechanism or measure. It does not by itself establish a causal effect.</p>
        </>
      ) : selectedNode ? (
        <>
          <p className="eyebrow">Node</p>
          <h2>{selectedNode.data.name}</h2>
          <dl>
            <Field label="Category" value={selectedNode.data.category} />
            <Field label="Level" value={selectedNode.data.level} />
            <Field label="Description" value={selectedNode.data.description} />
          </dl>
        </>
      ) : (
        <>
          <p className="eyebrow">Relationship</p>
          <h2>{selectedEdge.sourceName} → {selectedEdge.targetName}</h2>
          <dl>
            <Field label="Type" value={selectedEdge.data.type} />
            <Field label="Direction" value={selectedEdge.data.direction} />
            <Field label="Notation" value={selectedEdge.data.symbol} />
            <Field label="Evidence rating / confidence" value={selectedEdge.data.confidence} />
            <Field label="Evidence basis" value={selectedEdge.data.evidence_basis} />
            <Field label="Context notes" value={selectedEdge.data.notes} />
            <Field label="References" value={selectedEdge.data.references} />
            <Field label="Reviewed by" value={selectedEdge.data.reviewed_by} />
            <Field label="Last updated" value={selectedEdge.data.last_updated} />
          </dl>
        </>
      )}
    <div style={{ marginTop: 'auto', paddingTop: '2rem', textAlign: 'right' }}>
      <button 
        className="reset-btn" 
        onClick={() => window.location.reload()}
        style={{ marginTop: '1rem' }}
      >
        ✕ Reset view
      </button>
    </div>
    </aside>
  );
}

function Field({ label, value }) {
  return (
    <div className="detail">
      <dt>{label}</dt>
      <dd>{value || 'Not specified'}</dd>
    </div>
  );
}

export default function Sidebar({ selected }) {
  return (
    <aside className="sidebar" aria-label="Graph details">
      {!selected ? (
        <>
          <p className="eyebrow">Explore the evidence</p>
          <h2>Select a node or relationship</h2>
          <p>Click an item to see its context and source information. Zoom and pan to explore the map.</p>
          <p className="notice">A relationship describes a menu-reported component, mechanism or measure. It does not by itself establish a causal effect.</p>
        </>
      ) : selected.kind === 'node' ? (
        <>
          <p className="eyebrow">Node</p>
          <h2>{selected.data.name}</h2>
          <dl>
            <Field label="Category" value={selected.data.category} />
            <Field label="Level" value={selected.data.level} />
            <Field label="Description" value={selected.data.description} />
          </dl>
        </>
      ) : (
        <>
          <p className="eyebrow">Relationship</p>
          <h2>{selected.sourceName} → {selected.targetName}</h2>
          <dl>
            <Field label="Type" value={selected.data.type} />
            <Field label="Direction" value={selected.data.direction} />
            <Field label="Notation" value={selected.data.symbol} />
            <Field label="Evidence rating / confidence" value={selected.data.confidence} />
            <Field label="Evidence basis" value={selected.data.evidence_basis} />
            <Field label="Context notes" value={selected.data.notes} />
            <Field label="References" value={selected.data.references} />
            <Field label="Reviewed by" value={selected.data.reviewed_by} />
            <Field label="Last updated" value={selected.data.last_updated} />
          </dl>
        </>
      )}
    </aside>
  );
}

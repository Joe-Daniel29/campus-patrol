export default function Panel({ title, count, children }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <span>{title}</span>
        {count !== undefined && <span className="mono">{count}</span>}
      </div>
      <div className="panel-body">{children}</div>
    </section>
  );
}

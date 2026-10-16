import Panel from "./Panel.jsx";
import { label, timeAgo } from "../format.js";

function Battery({ value }) {
  const level = value < 15 ? "critical" : value < 30 ? "low" : "";
  return (
    <>
      <span className={`battery ${level}`}><span style={{ width: `${value}%` }} /></span>
      <span className="mono">{Math.round(value)}%</span>
    </>
  );
}

export default function RoversPanel({ rovers }) {
  return (
    <Panel title="Rovers" count={rovers.length}>
      {rovers.length === 0 ? (
        <div className="empty">No rovers registered.</div>
      ) : (
        <table>
          <thead>
            <tr><th>Name</th><th>Status</th><th>Battery</th><th>Last seen</th></tr>
          </thead>
          <tbody>
            {rovers.map((r) => (
              <tr key={r.id}>
                <td className="mono">{r.name}</td>
                <td>{r.online ? label(r.status) : <span className="muted">offline</span>}</td>
                <td><Battery value={r.battery} /></td>
                <td className="mono muted">{timeAgo(r.last_seen)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Panel>
  );
}

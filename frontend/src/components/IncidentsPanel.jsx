import Panel from "./Panel.jsx";
import { timeAgo } from "../format.js";

export default function IncidentsPanel({ incidents, onUpdate }) {
  return (
    <Panel title="Incidents" count={incidents.length}>
      {incidents.length === 0 ? (
        <div className="empty">No incidents.</div>
      ) : (
        <table>
          <thead>
            <tr><th>Status</th><th>Severity</th><th>Title</th><th>Zone</th><th>Age</th><th /></tr>
          </thead>
          <tbody>
            {incidents.map((i) => (
              <tr key={i.id}>
                <td><span className={`tag ${i.status}`}>{i.status}</span></td>
                <td><span className={`tag ${i.severity}`}>{i.severity}</span></td>
                <td>{i.title}</td>
                <td>{i.zone_name || <span className="muted">-</span>}</td>
                <td className="mono muted">{timeAgo(i.created_at)}</td>
                <td>
                  {i.status === "OPEN" && (
                    <button onClick={() => onUpdate(i.id, { status: "ACKNOWLEDGED", assignee: "security-desk" })}>
                      Acknowledge
                    </button>
                  )}
                  {i.status !== "RESOLVED" && (
                    <button onClick={() => onUpdate(i.id, { status: "RESOLVED" })}>Resolve</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Panel>
  );
}

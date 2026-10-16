import Panel from "./Panel.jsx";
import { label, timeAgo } from "../format.js";

export default function EventsPanel({ events }) {
  return (
    <Panel title="Events" count={events.length}>
      {events.length === 0 ? (
        <div className="empty">No events yet.</div>
      ) : (
        <table>
          <thead>
            <tr><th>Time</th><th>Severity</th><th>Type</th><th>Rover</th><th>Zone</th><th>Conf.</th></tr>
          </thead>
          <tbody>
            {events.map((e) => (
              <tr key={e.id} title={e.message}>
                <td className="mono muted">{timeAgo(e.created_at)}</td>
                <td><span className={`tag ${e.severity}`}>{e.severity}</span></td>
                <td>{label(e.type)}</td>
                <td className="mono">{e.rover_name}</td>
                <td>{e.zone_name || <span className="muted">-</span>}</td>
                <td className="mono">{e.confidence.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Panel>
  );
}

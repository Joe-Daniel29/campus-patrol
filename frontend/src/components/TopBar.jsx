import { timeAgo } from "../format.js";

function Metric({ name, value }) {
  return (
    <div className="metric">
      <span className="muted">{name}</span>
      <span className="value">{value}</span>
    </div>
  );
}

export default function TopBar({ stats, connected, updatedAt }) {
  return (
    <header className="topbar">
      <h1>Campus Patrol</h1>
      <div className="metrics">
        <Metric name="rovers online" value={stats ? `${stats.rovers_online}/${stats.rovers_total}` : "-"} />
        <Metric name="open incidents" value={stats ? stats.incidents_open : "-"} />
        <Metric name="events (1h)" value={stats ? stats.events_last_hour : "-"} />
      </div>
      <div className="conn">
        <span className={`dot ${connected ? "ok" : "crit"}`} />
        <span>{connected ? "live" : "disconnected"}</span>
        {updatedAt && <span className="mono">{timeAgo(updatedAt.toISOString())}</span>}
      </div>
    </header>
  );
}

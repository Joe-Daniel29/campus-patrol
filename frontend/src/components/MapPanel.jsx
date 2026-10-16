import Panel from "./Panel.jsx";

function roverColour(rover) {
  if (!rover.online) return "#6b6d75";
  if (rover.status === "CHARGING") return "#d9a441";
  if (rover.status === "RESPONDING") return "#e05d5d";
  return "#8b7bf0";
}

export default function MapPanel({ zones, rovers }) {
  const width = Math.max(100, ...zones.map((z) => z.x + z.width)) + 20;
  const height = Math.max(100, ...zones.map((z) => z.y + z.height)) + 20;

  return (
    <Panel title="Map" count={`${width - 20} x ${height - 20} m`}>
      <svg className="map" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="xMidYMid meet">
        {zones.map((z) => (
          <g key={z.id}>
            <rect className="zone" x={z.x} y={z.y} width={z.width} height={z.height} rx="3" />
            <text className="zone-label" x={z.x + 6} y={z.y + 14}>{z.name}</text>
          </g>
        ))}
        {rovers.map((r) => {
          const rad = (r.heading * Math.PI) / 180;
          const colour = roverColour(r);
          return (
            <g key={r.id}>
              <line
                x1={r.x}
                y1={r.y}
                x2={r.x + 12 * Math.cos(rad)}
                y2={r.y + 12 * Math.sin(rad)}
                stroke={colour}
                strokeWidth="2"
              />
              <circle cx={r.x} cy={r.y} r="5" fill={colour} />
              <text className="rover-label" x={r.x + 8} y={r.y - 8}>{r.name}</text>
            </g>
          );
        })}
      </svg>
    </Panel>
  );
}

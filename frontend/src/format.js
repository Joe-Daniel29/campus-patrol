export function timeAgo(iso) {
  if (!iso) return "never";
  // The API returns UTC timestamps; SQLite deployments may omit the zone suffix.
  const stamp = /[zZ]|[+-]\d\d:\d\d$/.test(iso) ? iso : `${iso}Z`;
  const seconds = Math.max(0, Math.round((Date.now() - new Date(stamp).getTime()) / 1000));
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

export function label(value) {
  return value.toLowerCase().replace(/_/g, " ");
}

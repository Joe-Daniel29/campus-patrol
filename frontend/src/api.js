async function request(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) throw new Error(`${options?.method || "GET"} ${path} -> ${response.status}`);
  return response.status === 204 ? null : response.json();
}

export async function loadSnapshot() {
  const [stats, rovers, zones, events, incidents] = await Promise.all([
    request("/api/stats"),
    request("/api/rovers"),
    request("/api/zones"),
    request("/api/events?limit=50"),
    request("/api/incidents"),
  ]);
  return { stats, rovers, zones, events, incidents };
}

export function updateIncident(id, body) {
  return request(`/api/incidents/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

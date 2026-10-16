import { useCallback, useEffect, useState } from "react";
import { loadSnapshot, updateIncident } from "./api.js";
import TopBar from "./components/TopBar.jsx";
import MapPanel from "./components/MapPanel.jsx";
import RoversPanel from "./components/RoversPanel.jsx";
import EventsPanel from "./components/EventsPanel.jsx";
import IncidentsPanel from "./components/IncidentsPanel.jsx";

const POLL_MS = 3000;
const EMPTY = { stats: null, rovers: [], zones: [], events: [], incidents: [] };

export default function App() {
  const [data, setData] = useState(EMPTY);
  const [connected, setConnected] = useState(false);
  const [updatedAt, setUpdatedAt] = useState(null);

  const refresh = useCallback(async () => {
    try {
      setData(await loadSnapshot());
      setConnected(true);
      setUpdatedAt(new Date());
    } catch {
      setConnected(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, POLL_MS);
    return () => clearInterval(timer);
  }, [refresh]);

  const handleIncidentUpdate = async (id, body) => {
    await updateIncident(id, body);
    refresh();
  };

  return (
    <>
      <TopBar stats={data.stats} connected={connected} updatedAt={updatedAt} />
      {!connected && <div className="banner">Cannot reach the API. Retrying every few seconds.</div>}
      <main className="layout">
        <MapPanel zones={data.zones} rovers={data.rovers} />
        <RoversPanel rovers={data.rovers} />
        <EventsPanel events={data.events} />
        <IncidentsPanel incidents={data.incidents} onUpdate={handleIncidentUpdate} />
      </main>
    </>
  );
}

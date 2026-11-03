import { AppShell } from "./components/layout/AppShell";
import { useHashRoute } from "./hooks/useHashRoute";
import { ActivityPage } from "./pages/ActivityPage";
import { OverviewPage } from "./pages/OverviewPage";
import { SettingsPage } from "./pages/SettingsPage";
import { TicketsPage } from "./pages/TicketsPage";

export default function App() {
  const route = useHashRoute();
  return (
    <AppShell route={route.name}>
      {route.name === "overview" && <OverviewPage />}
      {route.name === "tickets" && <TicketsPage ticketId={route.ticketId} />}
      {route.name === "activity" && <ActivityPage />}
      {route.name === "settings" && <SettingsPage />}
    </AppShell>
  );
}

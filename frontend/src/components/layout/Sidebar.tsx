import { Activity, LayoutDashboard, Settings, Ticket } from "lucide-react";
import { useHealth } from "../../hooks/useHealth";
import type { RouteName } from "../../hooks/useHashRoute";
import { cx } from "../../utils/format";

const items: Array<{ route: RouteName; label: string; href: string; icon: typeof Ticket }> = [
  { route: "overview", label: "Overview", href: "#/", icon: LayoutDashboard },
  { route: "tickets", label: "All Tickets", href: "#/tickets", icon: Ticket },
  { route: "activity", label: "Agent Activity", href: "#/activity", icon: Activity },
  { route: "settings", label: "Settings", href: "#/settings", icon: Settings },
];

function AiStatus() {
  const { health, error, loading } = useHealth();
  const configured = health?.llm_configured ?? false;
  const tone = loading ? "processing" : error ? "danger" : configured ? "success" : "warning";
  const label = loading
    ? "Checking AI…"
    : error
      ? "AI unreachable"
      : configured
        ? `AI ready · ${health?.llm_model?.split("/")[1] ?? "connected"}`
        : "AI not configured";

  return (
    <div className="mx-3 mb-3 rounded-lg border border-line bg-subtle/50 px-3 py-2.5">
      <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">Status</p>
      <p
        className={cx(
          "mt-1 flex items-center gap-1.5 text-xs font-medium",
          tone === "success" && "text-success",
          tone === "warning" && "text-warning",
          tone === "danger" && "text-danger",
          tone === "processing" && "text-processing",
        )}
      >
        <span
          className={cx(
            "h-1.5 w-1.5 rounded-full",
            tone === "success" && "bg-success",
            tone === "warning" && "bg-warning",
            tone === "danger" && "bg-danger",
            tone === "processing" && "bg-processing animate-pulse",
          )}
        />
        {label}
      </p>
    </div>
  );
}

export function Sidebar({ route }: { route: RouteName }) {
  return (
    <aside className="shrink-0 border-b border-line bg-surface md:flex md:w-64 md:flex-col md:border-b-0 md:border-r">
      <div className="px-5 py-5 md:py-6">
        <p className="text-base font-bold tracking-tight text-ink">SupportAgent Desk</p>
        <p className="mt-0.5 text-[11px] font-medium uppercase tracking-wider text-faint">
          AI Triage Console
        </p>
      </div>
      <nav aria-label="Main" className="flex gap-1 overflow-x-auto px-3 pb-3 md:flex-col md:pb-0">
        {items.map(({ route: name, label, href, icon: Icon }) => (
          <a
            key={name}
            href={href}
            aria-current={route === name ? "page" : undefined}
            className={cx(
              "flex items-center gap-2.5 whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium transition-colors",
              route === name
                ? "bg-primary-soft text-primary"
                : "text-muted hover:bg-subtle hover:text-ink",
            )}
          >
            <Icon size={17} aria-hidden="true" />
            {label}
          </a>
        ))}
      </nav>
      <div className="hidden md:mt-auto md:block md:pb-3">
        <AiStatus />
      </div>
    </aside>
  );
}
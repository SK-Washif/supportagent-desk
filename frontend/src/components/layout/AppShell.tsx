import type { ReactNode } from "react";
import type { RouteName } from "../../hooks/useHashRoute";
import { Sidebar } from "./Sidebar";

export function AppShell({ route, children }: { route: RouteName; children: ReactNode }) {
  return (
    <div className="flex min-h-full flex-col md:flex-row">
      <Sidebar route={route} />
      <main className="min-w-0 flex-1 px-4 py-6 md:px-8 md:py-8">
        <div className="mx-auto max-w-6xl">{children}</div>
      </main>
    </div>
  );
}

export function PageHeader({ title, description }: { title: string; description?: string }) {
  return (
    <header className="mb-6">
      <h1 className="text-xl font-semibold text-ink">{title}</h1>
      {description && <p className="mt-1 text-sm text-muted">{description}</p>}
    </header>
  );
}

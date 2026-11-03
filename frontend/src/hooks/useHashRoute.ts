import { useEffect, useState } from "react";

export type RouteName = "overview" | "tickets" | "activity" | "settings";

export interface Route {
  name: RouteName;
  ticketId: string | null;
}

function parse(hash: string): Route {
  const [, first = "", second = ""] = hash.replace(/^#/, "").split("/");
  if (first === "tickets") return { name: "tickets", ticketId: second ? decodeURIComponent(second) : null };
  if (first === "activity") return { name: "activity", ticketId: null };
  if (first === "settings") return { name: "settings", ticketId: null };
  return { name: "overview", ticketId: null };
}

export function useHashRoute(): Route {
  const [route, setRoute] = useState<Route>(() => parse(window.location.hash));
  useEffect(() => {
    const onChange = () => setRoute(parse(window.location.hash));
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);
  return route;
}

export function ticketHref(ticketId: string): string {
  return `#/tickets/${encodeURIComponent(ticketId)}`;
}

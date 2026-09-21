import { useEffect, useState } from "react";

/** Hash routing keeps deep links working on Vercel Services, where every non-/api path is served by the static frontend root. */
export type RouteName = "overview" | "review" | "drugs" | "drug" | "labs" | "activity" | "about" | "notfound";
export interface Route { name: RouteName; id?: string }

export function parseHash(hash: string): Route {
  const path = hash.replace(/^#/, "").split("?")[0].replace(/\/+$/, "") || "/";
  const parts = path.split("/").filter(Boolean);
  if (parts.length === 0) return { name: "overview" };
  if (parts[0] === "review" && parts.length === 1) return { name: "review" };
  if (parts[0] === "drugs" && parts.length === 1) return { name: "drugs" };
  if (parts[0] === "drugs" && parts.length === 2) return { name: "drug", id: decodeURIComponent(parts[1]) };
  if (parts[0] === "lab-trends" && parts.length === 1) return { name: "labs" };
  if (parts[0] === "activity" && parts.length === 1) return { name: "activity" };
  if (parts[0] === "about" && parts.length === 1) return { name: "about" };
  return { name: "notfound" };
}

export function useRoute(): Route {
  const [route, setRoute] = useState<Route>(() => parseHash(window.location.hash));
  useEffect(() => {
    const on = () => setRoute(parseHash(window.location.hash));
    window.addEventListener("hashchange", on);
    return () => window.removeEventListener("hashchange", on);
  }, []);
  return route;
}

export const href = (path: string) => `#${path}`;
export const navigate = (path: string) => { window.location.hash = path; };

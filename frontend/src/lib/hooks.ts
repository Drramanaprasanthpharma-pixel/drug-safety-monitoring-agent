import { useEffect, useState } from "react";
import { api } from "../api";
import type { DrugSummary } from "../types";

export function useMedia(query: string): boolean {
  const [match, setMatch] = useState(() => window.matchMedia(query).matches);
  useEffect(() => {
    const mq = window.matchMedia(query);
    const on = () => setMatch(mq.matches);
    mq.addEventListener("change", on);
    on();
    return () => mq.removeEventListener("change", on);
  }, [query]);
  return match;
}

export type Health = "checking" | "online" | "offline";

export function useApiHealth(intervalMs = 30000): Health {
  const [health, setHealth] = useState<Health>("checking");
  useEffect(() => {
    let alive = true;
    const ping = () => api.health().then((r) => alive && setHealth(r.status === "ok" ? "online" : "offline")).catch(() => alive && setHealth("offline"));
    ping();
    const t = setInterval(ping, intervalMs);
    return () => { alive = false; clearInterval(t); };
  }, [intervalMs]);
  return health;
}

/** Debounced GET /api/drugs?q= with cancellation of stale requests. */
export function useDrugSearch(query: string, enabled: boolean) {
  const [state, setState] = useState<{ results: DrugSummary[]; loading: boolean; error: boolean }>({ results: [], loading: false, error: false });
  useEffect(() => {
    if (!enabled) return;
    const ctl = new AbortController();
    const t = window.setTimeout(async () => {
      setState((s) => ({ ...s, loading: true, error: false }));
      try {
        const results = await api.searchDrugs(query.trim(), ctl.signal);
        setState({ results: results.slice(0, 8), loading: false, error: false });
      } catch (e) {
        if (e instanceof DOMException && e.name === "AbortError") return;
        setState({ results: [], loading: false, error: true });
      }
    }, 160);
    return () => { window.clearTimeout(t); ctl.abort(); };
  }, [query, enabled]);
  return state;
}

/** Fetch-on-mount helper with retry, used by pages that read a single resource. */
export function useAsync<T>(load: () => Promise<T>, deps: unknown[]) {
  const [state, setState] = useState<{ data: T | null; error: unknown; loading: boolean }>({ data: null, error: null, loading: true });
  const [nonce, setNonce] = useState(0);
  useEffect(() => {
    let alive = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    load().then((data) => alive && setState({ data, error: null, loading: false }))
      .catch((error) => alive && setState({ data: null, error, loading: false }));
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce]);
  return { ...state, retry: () => setNonce((n) => n + 1) };
}

import { useEffect, useId, useRef, useState } from "react";
import { Icon } from "./icons";
import { href, navigate } from "../lib/route";
import { useApiHealth, useDrugSearch } from "../lib/hooks";
import { useStore } from "../lib/store";

export function GlobalSearch() {
  const [q, setQ] = useState("");
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const listId = useId();
  const { results, loading, error } = useDrugSearch(q, open && q.trim().length > 0);
  const shown = q.trim() ? results : [];

  const go = (id: string) => { setOpen(false); setQ(""); navigate(`/drugs/${encodeURIComponent(id)}`); };
  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") { e.preventDefault(); setActive((a) => Math.min(a + 1, shown.length - 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setActive((a) => Math.max(a - 1, 0)); }
    else if (e.key === "Enter" && shown[active]) { e.preventDefault(); go(shown[active].id); }
    else if (e.key === "Escape") setOpen(false);
  };

  return (
    <div className="search" role="search">
      <Icon name="search" size={18} />
      <input
        type="search" placeholder="Search drugs by generic or brand name" aria-label="Search drugs" role="combobox" autoComplete="off"
        aria-expanded={open && q.trim().length > 0} aria-controls={listId} aria-autocomplete="list"
        aria-activedescendant={shown[active] ? `${listId}-${shown[active].id}` : undefined}
        value={q} onChange={(e) => { setQ(e.target.value); setActive(0); setOpen(true); }}
        onFocus={() => setOpen(true)} onBlur={() => setOpen(false)} onKeyDown={onKey}
      />
      {open && q.trim() && (
        <div className="popover" id={listId} role="listbox" aria-label="Drug matches">
          {shown.map((d, i) => (
            <div key={d.id} id={`${listId}-${d.id}`} role="option" aria-selected={i === active} className="option"
              onMouseDown={(e) => { e.preventDefault(); go(d.id); }} onMouseEnter={() => setActive(i)}>
              <strong>{d.generic_name}</strong>
              <small>{d.drug_class}{d.brand_names.length ? ` · ${d.brand_names.join(", ")}` : ""}</small>
            </div>
          ))}
          {!shown.length && (
            <div className="option" role="option" aria-selected="false" style={{ cursor: "default" }}>
              {loading ? "Searching…" : error ? "Search is unavailable right now" : "No matching drug in the library"}
              {!loading && !error && <small>Only medications in the curated dataset can be found.</small>}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function ApiStatus() {
  const health = useApiHealth();
  const label = health === "online" ? "Service online" : health === "offline" ? "Service unreachable" : "Checking service";
  return (
    <div className="status" role="status" title={label}>
      <span className="dot" data-tone={health === "online" ? "ok" : health === "offline" ? "bad" : undefined} aria-hidden="true" />
      <span className="status-text">{label}</span>
    </div>
  );
}

/** Alerts = the red flags from the most recent review in this browser session (there is no server-side alert feed). */
export function AlertsMenu() {
  const { lastReview } = useStore();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const flags = lastReview?.result.red_flags ?? [];

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => { if (!ref.current?.contains(e.target as Node)) setOpen(false); };
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", onDoc);
    document.addEventListener("keydown", onKey);
    return () => { document.removeEventListener("mousedown", onDoc); document.removeEventListener("keydown", onKey); };
  }, [open]);

  return (
    <div ref={ref} style={{ position: "relative" }}>
      <button type="button" className="icon-btn" aria-haspopup="true" aria-expanded={open} aria-label={`Red flags from your last review${flags.length ? `, ${flags.length} found` : ""}`} onClick={() => setOpen((o) => !o)}>
        <Icon name="bell" />
        {flags.length > 0 && <span className="badge-count" aria-hidden="true">{flags.length}</span>}
      </button>
      {open && (
        <div className="popover right" role="dialog" aria-label="Red flags from your last review">
          <div className="popover-title">Red flags from your last review</div>
          {flags.length === 0 ? (
            <p className="option muted" style={{ cursor: "default" }}>
              {lastReview ? "The last review raised no red flags." : "Nothing yet. Run a safety review and any red flags will appear here."}
            </p>
          ) : (
            <>
              {flags.slice(0, 5).map((f, i) => (
                <a key={i} className="option" href={href("/review")} onClick={() => setOpen(false)}>
                  <strong>{f.trigger}</strong>
                  <small>{f.escalation}</small>
                </a>
              ))}
              {flags.length > 5 && <p className="option muted small" style={{ cursor: "default" }}>+{flags.length - 5} more in the review</p>}
            </>
          )}
        </div>
      )}
    </div>
  );
}

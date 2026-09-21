import { useId, useState, type KeyboardEvent } from "react";
import { Icon } from "./icons";
import { useDrugSearch } from "../lib/hooks";
import type { PickedDrug } from "../lib/store";

export const MAX_DRUGS = 15; // matches the /api/analyze limit

export function DrugPicker({ value, onChange, label = "Medications to review", hideLabel }: {
  value: PickedDrug[]; onChange: (next: PickedDrug[]) => void; label?: string; hideLabel?: boolean;
}) {
  const [q, setQ] = useState("");
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const listId = useId();
  const inputId = useId();
  const { results, loading, error } = useDrugSearch(q, open);
  const picked = new Set(value.map((v) => v.id ?? v.label.toLowerCase()));
  const options = results.filter((r) => !picked.has(r.id));
  const full = value.length >= MAX_DRUGS;

  const add = (d: PickedDrug) => {
    if (full || picked.has(d.id ?? d.label.toLowerCase())) return;
    onChange([...value, d]);
    setQ(""); setActive(0);
  };
  const remove = (key: string) => onChange(value.filter((v) => v.key !== key));

  const onKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "ArrowDown") { e.preventDefault(); setOpen(true); setActive((a) => Math.min(a + 1, options.length - 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setActive((a) => Math.max(a - 1, 0)); }
    else if (e.key === "Escape") setOpen(false);
    else if (e.key === "Enter") {
      if (!q.trim() && !options[active]) return; // let the form submit
      e.preventDefault();
      const opt = options[active];
      if (opt && open) add({ key: opt.id, id: opt.id, label: opt.generic_name });
      else if (q.trim()) add({ key: `text:${q.trim().toLowerCase()}`, label: q.trim() });
    } else if (e.key === "Backspace" && !q && value.length) remove(value[value.length - 1].key);
  };

  return (
    <div className="picker-box">
      <div className="field">
        <label htmlFor={inputId} className={hideLabel ? "sr-only" : undefined}>{label}</label>
        <div className="combo">
          <Icon name="search" size={18} />
          <input
            id={inputId} className="input" type="text" role="combobox" autoComplete="off" value={q} disabled={full}
            placeholder={full ? `Limit of ${MAX_DRUGS} medications reached` : "Type a generic or brand name, e.g. warfarin or Coumadin"}
            aria-expanded={open} aria-controls={listId} aria-autocomplete="list" aria-describedby={`${inputId}-hint`}
            aria-activedescendant={open && options[active] ? `${listId}-${options[active].id}` : undefined}
            onChange={(e) => { setQ(e.target.value); setActive(0); setOpen(true); }}
            onFocus={() => setOpen(true)} onBlur={() => setOpen(false)} onKeyDown={onKey}
          />
          {open && !full && (
            <div className="popover" id={listId} role="listbox" aria-label="Matching medications">
              {options.map((d, i) => (
                <div key={d.id} id={`${listId}-${d.id}`} role="option" aria-selected={i === active} className="option"
                  onMouseDown={(e) => { e.preventDefault(); add({ key: d.id, id: d.id, label: d.generic_name }); }} onMouseEnter={() => setActive(i)}>
                  <strong>{d.generic_name}</strong>
                  <small>{d.drug_class}{d.brand_names.length ? ` · ${d.brand_names.join(", ")}` : ""}</small>
                </div>
              ))}
              {!options.length && (
                <div className="option" role="option" aria-selected="false" style={{ cursor: "default" }}>
                  {loading ? "Searching…" : error ? "Search is unavailable. Press Enter to add what you typed." : q.trim() ? `No match for “${q.trim()}”` : "All available medications are already added"}
                  {!loading && !error && q.trim() && <small>Press Enter to add it anyway — the service will confirm whether it recognizes the name.</small>}
                </div>
              )}
            </div>
          )}
        </div>
        <p className="hint" id={`${inputId}-hint`}>{value.length} of {MAX_DRUGS} added. Brand names are matched to their generic drug.</p>
      </div>
      {value.length > 0 && (
        <ul className="chips" style={{ marginTop: 12 }} aria-label="Selected medications">
          {value.map((d) => (
            <li key={d.key} className="chip">
              {d.label}
              <button type="button" aria-label={`Remove ${d.label}`} onClick={() => remove(d.key)}><Icon name="x" size={14} /></button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

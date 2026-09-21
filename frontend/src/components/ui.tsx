import { useRef, useState, type KeyboardEvent, type ReactNode } from "react";
import type { Confidence, InteractionSeverity, Level } from "../types";
import { Icon, type IconName } from "./icons";
import { href } from "../lib/route";

export function Sev({ level, label }: { level: Level | InteractionSeverity | string; label?: string }) {
  return <span className="sev" data-level={level}>{label ?? level}</span>;
}

export function ConfTag({ confidence }: { confidence: Confidence }) {
  return <span className="tag" data-conf={confidence}>{confidence} confidence</span>;
}

/** Marks curated-rules output (established facts) vs. AI-assisted prioritisation, mirroring the backend's own labels. */
export const RulesTag = () => <span className="tag tag-rules">Rules engine · curated data</span>;
export const AiTag = ({ children = "AI-assisted prioritization" }: { children?: ReactNode }) => (
  <span className="tag tag-ai"><Icon name="spark" size={13} />{children}</span>
);
export const DemoTag = () => <span className="tag tag-demo">Demo data</span>;

export function Panel({ title, subtitle, actions, children, flush, id }: {
  title?: ReactNode; subtitle?: ReactNode; actions?: ReactNode; children: ReactNode; flush?: boolean; id?: string;
}) {
  return (
    <section className="panel" aria-labelledby={title && id ? `${id}-h` : undefined}>
      {(title || actions) && (
        <header className="panel-head">
          <div>
            {title && <h2 id={id ? `${id}-h` : undefined} style={{ fontSize: 18 }}>{title}</h2>}
            {subtitle && <p>{subtitle}</p>}
          </div>
          {actions && <div className="row">{actions}</div>}
        </header>
      )}
      <div className={flush ? "panel-flush" : "panel-body"}>{children}</div>
    </section>
  );
}

export function Notice({ tone, icon = "info", children }: { tone?: "demo" | "bad"; icon?: IconName; children: ReactNode }) {
  return (
    <div className="notice" data-tone={tone} role={tone === "bad" ? "alert" : undefined}>
      <Icon name={icon} size={18} />
      <div>{children}</div>
    </div>
  );
}

/* --------------------------------------------------------------------- tabs */
export interface TabDef { id: string; label: string; count?: number; alert?: boolean }

export function Tabs({ tabs, value, onChange, idBase, label }: {
  tabs: TabDef[]; value: string; onChange: (id: string) => void; idBase: string; label: string;
}) {
  const refs = useRef<Record<string, HTMLButtonElement | null>>({});
  const move = (e: KeyboardEvent, i: number) => {
    let n = i;
    if (e.key === "ArrowRight") n = (i + 1) % tabs.length;
    else if (e.key === "ArrowLeft") n = (i - 1 + tabs.length) % tabs.length;
    else if (e.key === "Home") n = 0;
    else if (e.key === "End") n = tabs.length - 1;
    else return;
    e.preventDefault();
    onChange(tabs[n].id);
    refs.current[tabs[n].id]?.focus();
  };
  return (
    <div className="tabs no-print" role="tablist" aria-label={label}>
      {tabs.map((t, i) => (
        <button
          key={t.id} type="button" role="tab" className="tab" id={`${idBase}-tab-${t.id}`} ref={(el) => { refs.current[t.id] = el; }}
          aria-selected={value === t.id} aria-controls={`${idBase}-panel-${t.id}`} tabIndex={value === t.id ? 0 : -1}
          onClick={() => onChange(t.id)} onKeyDown={(e) => move(e, i)}
        >
          {t.label}
          {t.count !== undefined && <span className="n" data-alert={t.alert ? "true" : undefined}>{t.count}</span>}
        </button>
      ))}
    </div>
  );
}

export function TabPanel({ idBase, id, active, children }: { idBase: string; id: string; active: boolean; children: ReactNode }) {
  return (
    <div role="tabpanel" className="tabpanel" id={`${idBase}-panel-${id}`} aria-labelledby={`${idBase}-tab-${id}`} hidden={!active}>
      {children}
    </div>
  );
}

/* ------------------------------------------------------------------- states */
export function EmptyState({ icon = "info", title, children, action }: { icon?: IconName; title: string; children?: ReactNode; action?: ReactNode }) {
  return (
    <div className="state">
      <div className="state-icon"><Icon name={icon} size={24} /></div>
      <h2>{title}</h2>
      {children && <p>{children}</p>}
      {action}
    </div>
  );
}

export function ErrorState({ title = "Unable to complete this request", message, detail, onRetry, homeLink = true }: {
  title?: string; message: string; detail?: string; onRetry?: () => void; homeLink?: boolean;
}) {
  const [open, setOpen] = useState(false);
  return (
    <div className="state" data-tone="bad" role="alert">
      <div className="state-icon"><Icon name="alert" size={24} /></div>
      <h2>{title}</h2>
      <p>{message}</p>
      <div className="row" style={{ justifyContent: "center" }}>
        {onRetry && <button type="button" className="btn btn-primary" onClick={onRetry}><Icon name="refresh" size={16} />Retry</button>}
        {detail && <button type="button" className="btn" aria-expanded={open} onClick={() => setOpen((o) => !o)}>{open ? "Hide details" : "View details"}</button>}
        {homeLink && <a className="btn btn-ghost" href={href("/")}>Return to overview</a>}
      </div>
      {open && detail && <pre>{detail}</pre>}
    </div>
  );
}

/** Skeleton + honest status text. It never claims progress the backend is not reporting. */
export function LoadingState({ message, rows = 3 }: { message: string; rows?: number }) {
  return (
    <div className="stack" role="status" aria-live="polite" aria-busy="true">
      <div className="loading-note"><span className="spinner" aria-hidden="true" />{message}</div>
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="panel panel-pad stack" aria-hidden="true">
          <span className="skel" style={{ width: `${34 + ((i * 13) % 30)}%`, height: 18 }} />
          <span className="skel" style={{ width: "92%" }} />
          <span className="skel" style={{ width: "76%" }} />
        </div>
      ))}
    </div>
  );
}

export function PageHead({ title, children, actions }: { title: string; children?: ReactNode; actions?: ReactNode }) {
  return (
    <div className="page-head">
      <div>
        <h1>{title}</h1>
        {children && <p>{children}</p>}
      </div>
      {actions && <div className="page-actions">{actions}</div>}
    </div>
  );
}

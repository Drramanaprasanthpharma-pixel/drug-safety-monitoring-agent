import { useEffect, useRef, useState, type ReactNode } from "react";
import { Icon, type IconName } from "./icons";
import { AlertsMenu, ApiStatus, GlobalSearch } from "./TopBarWidgets";
import { href, type Route } from "../lib/route";
import { useMedia } from "../lib/hooks";

interface NavItem { path: string; label: string; icon: IconName; match: Route["name"][] }
const NAV: { title: string; items: NavItem[] }[] = [
  { title: "Review", items: [
    { path: "/", label: "Overview", icon: "layout", match: ["overview"] },
    { path: "/review", label: "Safety review", icon: "review", match: ["review"] },
    { path: "/lab-trends", label: "Lab trends", icon: "trend", match: ["labs"] },
  ] },
  { title: "Reference", items: [{ path: "/drugs", label: "Drug library", icon: "pill", match: ["drugs", "drug"] }] },
  { title: "System", items: [
    { path: "/activity", label: "Activity log", icon: "history", match: ["activity"] },
    { path: "/about", label: "About and limits", icon: "info", match: ["about"] },
  ] },
];

const SECTION: Record<Route["name"], string> = {
  overview: "Overview", review: "Safety review", labs: "Lab trends", drugs: "Drug library", drug: "Drug library",
  activity: "Activity log", about: "About and limits", notfound: "Not found",
};

export function AppShell({ route, drugName, children }: { route: Route; drugName?: string; children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem("ps.sidebar") === "collapsed");
  const [drawer, setDrawer] = useState(false);
  const isMobile = useMedia("(max-width: 1023px)");
  const menuBtn = useRef<HTMLButtonElement>(null);
  const firstLink = useRef<HTMLAnchorElement>(null);
  const mainRef = useRef<HTMLElement>(null);
  const firstRoute = useRef(true);

  useEffect(() => { localStorage.setItem("ps.sidebar", collapsed ? "collapsed" : "expanded"); }, [collapsed]);
  useEffect(() => {
    setDrawer(false);
    if (firstRoute.current) { firstRoute.current = false; return; }
    mainRef.current?.focus({ preventScroll: true });
    window.scrollTo(0, 0);
  }, [route.name, route.id]);
  useEffect(() => {
    if (!drawer) return;
    firstLink.current?.focus();
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") { setDrawer(false); menuBtn.current?.focus(); } };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [drawer]);

  const hidden = isMobile && !drawer;
  const inertProps = (hidden ? { inert: "" } : {}) as Record<string, string>;

  return (
    <div className="app" data-collapsed={collapsed && !isMobile} data-drawer={drawer ? "open" : "closed"}>
      <a className="skip-link" href="#main">Skip to content</a>
      <aside className="sidebar" aria-label="Primary" {...inertProps}>
        <a className="brand" href={href("/")} aria-label="PharmaSafe AI, go to overview">
          <span className="brand-mark"><Icon name="shield" size={19} strokeWidth={2.4} /></span>
          <span className="brand-name">PharmaSafe AI</span>
        </a>
        <nav className="nav" aria-label="Main">
          {NAV.map((g, gi) => (
            <div className="nav-group" key={g.title}>
              <div className="nav-group-title" id={`nav-${gi}`}>{g.title}</div>
              <ul aria-labelledby={`nav-${gi}`}>
                {g.items.map((n, ii) => (
                  <li key={n.path}>
                    <a
                      className="nav-link" href={href(n.path)} title={n.label} ref={gi === 0 && ii === 0 ? firstLink : undefined}
                      aria-current={n.match.includes(route.name) ? "page" : undefined} aria-label={collapsed && !isMobile ? n.label : undefined}
                    >
                      <Icon name={n.icon} />
                      <span className="nav-label">{n.label}</span>
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>
        <div className="nav-foot">Prototype on a curated demo dataset. Decision support only — verify against current prescribing information.</div>
      </aside>
      <div className="scrim" onClick={() => setDrawer(false)} aria-hidden="true" />

      <div className="main">
        <header className="topbar">
          <button ref={menuBtn} type="button" className="icon-btn menu-btn" aria-label="Open navigation" aria-expanded={drawer} onClick={() => setDrawer(true)}><Icon name="menu" /></button>
          <button type="button" className="icon-btn collapse-btn" aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"} aria-pressed={collapsed} onClick={() => setCollapsed((c) => !c)}><Icon name="panel" /></button>
          <nav className="crumbs" aria-label="Breadcrumb">
            <a href={href("/")}>PharmaSafe AI</a>
            <Icon name="right" size={14} />
            {route.name === "drug" ? (
              <>
                <a href={href("/drugs")}>Drug library</a>
                <Icon name="right" size={14} />
                <span aria-current="page">{drugName ?? route.id}</span>
              </>
            ) : <span aria-current="page">{SECTION[route.name]}</span>}
          </nav>
          <div className="topbar-spacer" />
          <GlobalSearch />
          <ApiStatus />
          <AlertsMenu />
        </header>
        <main id="main" ref={mainRef} tabIndex={-1} className="content" style={{ outline: "none" }}>{children}</main>
      </div>
    </div>
  );
}

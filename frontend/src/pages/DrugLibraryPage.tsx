import { useMemo, useState } from "react";
import { api } from "../api";
import { ApiError } from "../api";
import { Icon } from "../components/icons";
import { EmptyState, ErrorState, LoadingState, PageHead } from "../components/ui";
import { useAsync } from "../lib/hooks";
import { href, navigate } from "../lib/route";
import { useStore } from "../lib/store";

export function DrugLibraryPage() {
  const { setDraft } = useStore();
  const { data, error, loading, retry } = useAsync(() => api.searchDrugs(""), []);
  const [q, setQ] = useState("");
  const [cls, setCls] = useState("");

  const classes = useMemo(() => [...new Set((data ?? []).map((d) => d.drug_class))].sort(), [data]);
  const rows = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return (data ?? []).filter((d) =>
      (!cls || d.drug_class === cls) &&
      (!needle || d.generic_name.toLowerCase().includes(needle) || d.brand_names.some((b) => b.toLowerCase().includes(needle))));
  }, [data, q, cls]);

  return (
    <div className="stack-lg">
      <PageHead title="Drug library">Curated reference monographs for every medication the service can review. Open one for its full safety profile.</PageHead>

      {loading && <LoadingState message="Loading the drug library…" rows={2} />}
      {error != null && <div className="panel"><ErrorState title="Unable to load the drug library" message={error instanceof ApiError ? error.message : "The library could not be loaded."} detail={error instanceof ApiError ? error.detail : undefined} onRetry={retry} /></div>}

      {data && (
        <section className="panel" aria-label="Medications">
          <div className="panel-head">
            <div className="row" style={{ flex: 1 }}>
              <div className="field" style={{ flex: "1 1 240px" }}>
                <label htmlFor="lib-q" className="sr-only">Filter by name</label>
                <input id="lib-q" className="input" type="search" placeholder="Filter by generic or brand name" value={q} onChange={(e) => setQ(e.target.value)} />
              </div>
              <div className="field" style={{ flex: "0 1 260px" }}>
                <label htmlFor="lib-c" className="sr-only">Therapeutic class</label>
                <select id="lib-c" className="select" value={cls} onChange={(e) => setCls(e.target.value)}>
                  <option value="">All therapeutic classes</option>
                  {classes.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
            </div>
            <span className="muted small" role="status">{rows.length} of {data.length} shown</span>
          </div>
          {rows.length === 0 ? (
            <EmptyState icon="search" title="No medications match" action={<button type="button" className="btn" onClick={() => { setQ(""); setCls(""); }}>Clear filters</button>}>
              Try a different name or clear the class filter.
            </EmptyState>
          ) : (
            <div className="table-wrap">
              <table className="rtable stack-mobile">
                <thead><tr><th>Drug</th><th>Therapeutic class</th><th>Brand names</th><th><span className="sr-only">Actions</span></th></tr></thead>
                <tbody>
                  {rows.map((d) => (
                    <tr key={d.id}>
                      <td data-label="Drug"><a className="row-link" href={href(`/drugs/${encodeURIComponent(d.id)}`)}>{d.generic_name}</a></td>
                      <td data-label="Therapeutic class">{d.drug_class}</td>
                      <td data-label="Brand names" className="muted">{d.brand_names.join(", ") || "—"}</td>
                      <td className="num">
                        <button type="button" className="btn btn-sm" onClick={() => { setDraft({ drugs: [{ key: d.id, id: d.id, label: d.generic_name }], autoRun: true }); navigate("/review"); }}>
                          <Icon name="play" size={14} />Review
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </div>
  );
}

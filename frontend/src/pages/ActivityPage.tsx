import { api, ApiError } from "../api";
import { EmptyState, ErrorState, LoadingState, Notice, PageHead, DemoTag } from "../components/ui";
import { useAsync } from "../lib/hooks";
import { href, navigate } from "../lib/route";
import { useStore } from "../lib/store";
import { formatDateTime } from "../lib/format";

export function ActivityPage() {
  const { setDraft } = useStore();
  const { data, error, loading, retry } = useAsync(() => api.audit(50), []);
  return (
    <div className="stack-lg">
      <PageHead title="Activity log">Every review the service has run. Only drug names and whether patient context was supplied are recorded — never patient details.</PageHead>
      <Notice icon="info">This is a demo audit trail. On Vercel it lives in temporary storage and resets between deployments, so it is not a durable record.</Notice>
      {loading && <LoadingState message="Loading recent reviews…" rows={1} />}
      {error != null && <div className="panel"><ErrorState title="Unable to load the activity log" message={error instanceof ApiError ? error.message : "The log could not be loaded."} detail={error instanceof ApiError ? error.detail : undefined} onRetry={retry} /></div>}
      {data && (
        <section className="panel" aria-label="Reviews">
          {data.length === 0 ? (
            <EmptyState icon="history" title="No reviews logged yet" action={<a className="btn btn-primary" href={href("/review")}>Start a safety review</a>}>Reviews you run will appear here.</EmptyState>
          ) : (
            <div className="table-wrap">
              <table className="rtable stack-mobile">
                <thead><tr><th>When</th><th>Medications</th><th>Patient context</th><th>Data</th><th>Reference</th><th><span className="sr-only">Actions</span></th></tr></thead>
                <tbody>
                  {data.map((e) => (
                    <tr key={e.id}>
                      <td data-label="When">{formatDateTime(e.timestamp)}</td>
                      <td data-label="Medications"><strong>{e.drugs.join(" + ") || "—"}</strong></td>
                      <td data-label="Patient context">{e.patientProvided === null ? "—" : e.patientProvided ? "Provided" : "Drug-only"}</td>
                      <td data-label="Data">{e.demo ? <DemoTag /> : "—"}</td>
                      <td data-label="Reference" className="mono small">{e.id}</td>
                      <td className="num">{e.drugs.length > 0 && <button type="button" className="btn btn-sm" onClick={() => { setDraft({ drugs: e.drugs.map((d) => ({ key: d, id: d, label: d })), autoRun: true }); navigate("/review"); }}>Run again</button>}</td>
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

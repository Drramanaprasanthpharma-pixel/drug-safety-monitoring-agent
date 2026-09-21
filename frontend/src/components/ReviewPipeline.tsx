import type { AnalysisRequest, AnalysisResponse } from "../types";
import { Icon } from "./icons";
import { plural } from "../lib/format";

/** A record of the backend stages that actually ran, filled with the real counts from the response. It is shown after
 *  the review completes because /api/analyze is a single request and reports no live progress. */
export function ReviewPipeline({ result, request }: { result: AnalysisResponse; request: AnalysisRequest }) {
  const n = result.drugs_analyzed.length;
  const pairs = (n * (n - 1)) / 2;
  const steps: [string, string][] = [
    ["Medications normalized", `${plural(n, "medication")} matched to the drug database: ${result.drugs_analyzed.join(", ")}.`],
    ["Interaction rules checked", `${plural(pairs, "pair")} compared with the curated ruleset; ${result.interactions.length} matched.`],
    ["Organ toxicity aggregated", `${plural(result.priority_organs.length, "organ system")} ranked from labeling data.`],
    ["Patient context applied", request.patient
      ? `${plural(result.patient_risk_factors.length, "risk factor")} and ${plural(result.disease_interactions.length, "drug–disease match", "drug–disease matches")} found.`
      : "No patient context was supplied, so this was a drug-only review."],
    ["Red-flag rules evaluated", `${plural(result.red_flags.length, "red flag")} raised.`],
    ["Risk prioritization", `Score ${result.overall_risk.priority_score}/100, category ${result.overall_risk.category}.`],
    ["Actions and evidence compiled", `${plural(result.pharmacist_actions.length, "suggested action")} and ${plural(result.evidence.length, "evidence source")}.`],
    ["Audit record written", `Reference ${result.audit_id}. Only drug names and a patient-context flag are logged.`],
  ];
  return (
    <ol className="pipeline" aria-label="Completed review stages">
      {steps.map(([title, body]) => (
        <li className="pipe-step" key={title}>
          <span className="pipe-mark"><Icon name="check" size={15} strokeWidth={2.6} /></span>
          <div><h3>{title}</h3><p>{body}</p></div>
        </li>
      ))}
    </ol>
  );
}

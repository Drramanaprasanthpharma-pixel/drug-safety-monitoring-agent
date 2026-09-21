import { AiTag, Notice, PageHead, Panel, RulesTag } from "../components/ui";

export function AboutPage() {
  return (
    <div className="stack-lg">
      <PageHead title="About and limits">What this tool does, where its facts come from, and what it should not be used for.</PageHead>
      <Notice icon="alert">
        PharmaSafe AI is a clinical decision-support prototype. It does not replace a pharmacist, a physician or official prescribing information.
        Check every recommendation against current labeling, institutional protocols and clinical guidelines before acting.
      </Notice>
      <div className="grid-2">
        <Panel title="Two kinds of output" id="kinds">
          <div className="stack">
            <div><div style={{ marginBottom: 6 }}><RulesTag /></div><p>Interactions, monitoring parameters, adverse effects and red flags come from a deterministic rules engine reading a curated dataset. Each carries its source and a confidence label.</p></div>
            <div><div style={{ marginBottom: 6 }}><AiTag /></div><p>The overall score and the organ priority numbers are a transparent weighted heuristic. They rank what to look at first; they are not validated clinical probabilities or incidence rates.</p></div>
          </div>
        </Panel>
        <Panel title="Known limits" id="limits">
          <ul className="bullets">
            <li>Only the curated demo medications are recognized. It is not connected to a live FDA or EMA feed or a licensed drug database.</li>
            <li>Only interaction pairs listed in the ruleset are reported. The service never guesses at a pair it has no rule for.</li>
            <li>Drug–disease matching uses keywords in free-text diagnoses, not ICD-10 codes.</li>
            <li>There is no sign-in and no durable database. Add both before using real patient data.</li>
          </ul>
        </Panel>
      </div>
      <Panel title="Privacy" id="privacy">
        <p>Patient details you enter are sent to the service for the review and are not saved by this interface. The activity log records only which drugs were reviewed, whether patient context was supplied, and which sources were cited.</p>
      </Panel>
    </div>
  );
}

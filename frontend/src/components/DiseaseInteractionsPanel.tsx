import type { DiseaseInteraction, PatientRiskFactor } from '../types'
import { EmptyState, EvidenceLine, Section } from './ui'

export function DiseaseInteractionsPanel({ items }: { items: DiseaseInteraction[] }) {
  if (items.length === 0) return null
  return (
    <Section title="Drug–disease interactions" eyebrow="Section 9">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="text-left border-b-2 border-ink-950">
            <th className="py-2 pr-4 font-medium">Condition</th>
            <th className="py-2 pr-4 font-medium">Drug</th>
            <th className="py-2 pr-4 font-medium">Risk</th>
            <th className="py-2 pr-4 font-medium">Recommendation</th>
          </tr>
        </thead>
        <tbody>
          {items.map((d, idx) => (
            <tr key={idx} className="border-b rule align-top">
              <td className="py-3 pr-4 whitespace-nowrap">{d.condition}</td>
              <td className="py-3 pr-4 font-medium whitespace-nowrap">{d.drug}</td>
              <td className="py-3 pr-4 max-w-xs">{d.risk}</td>
              <td className="py-3 pr-4 max-w-xs">
                {d.recommendation}
                <EvidenceLine evidence={d.evidence} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Section>
  )
}

export function PatientRiskPanel({ factors }: { factors: PatientRiskFactor[] }) {
  return (
    <Section title="Patient-specific risk analysis" eyebrow="Section 13">
      {factors.length === 0 ? (
        <EmptyState message="No patient-specific risk factors identified — add patient information above to enable this analysis." />
      ) : (
        <ul className="space-y-2">
          {factors.map((f, idx) => (
            <li key={idx} className="border border-ink-100 p-3 text-sm">
              <p className="font-medium">
                {f.factor}
                {f.affected_organ && <span className="text-ink-500 font-normal"> · affects {f.affected_organ}</span>}
              </p>
              <p className="text-ink-700">{f.detail}</p>
            </li>
          ))}
        </ul>
      )}
    </Section>
  )
}

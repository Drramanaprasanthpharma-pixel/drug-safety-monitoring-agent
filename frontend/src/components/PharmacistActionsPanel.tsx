import type { PharmacistAction } from '../types'
import { EvidenceLine, Section } from './ui'

export function PharmacistActionsPanel({ actions }: { actions: PharmacistAction[] }) {
  return (
    <Section title="Recommended pharmacist actions" eyebrow="Section 17">
      <ol className="space-y-3">
        {actions.map((a, idx) => (
          <li key={idx} className="border border-ink-100 p-3 text-sm">
            <p className="font-medium">{a.action}</p>
            <p className="text-ink-700">{a.rationale}</p>
            <EvidenceLine evidence={a.evidence} />
          </li>
        ))}
      </ol>
    </Section>
  )
}

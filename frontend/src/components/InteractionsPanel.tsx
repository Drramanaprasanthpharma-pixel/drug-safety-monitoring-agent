import type { InteractionResult } from '../types'
import { EmptyState, EvidenceLine, Section, SeverityBadge } from './ui'

export function InteractionsPanel({ interactions }: { interactions: InteractionResult[] }) {
  return (
    <Section title="Drug–drug interactions" eyebrow="Section 8">
      {interactions.length === 0 ? (
        <EmptyState message="No known interactions were identified between the selected medications." />
      ) : (
        <div className="space-y-4">
          {interactions.map((i, idx) => (
            <article key={idx} className="border border-ink-100 p-4">
              <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                <h3 className="font-display text-lg">
                  {i.drug_a} + {i.drug_b}
                </h3>
                <SeverityBadge level={i.severity} />
              </div>
              <dl className="grid sm:grid-cols-2 gap-x-6 gap-y-2 text-sm">
                <div>
                  <dt className="text-ink-500">Mechanism</dt>
                  <dd>{i.mechanism.join(', ')} — {i.mechanism_detail}</dd>
                </div>
                <div>
                  <dt className="text-ink-500">Clinical consequence</dt>
                  <dd>{i.clinical_consequence}</dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="text-ink-500">Recommended action</dt>
                  <dd>
                    <span className="font-medium">{i.recommended_action}.</span> {i.action_detail}
                  </dd>
                </div>
              </dl>
              <EvidenceLine evidence={i.evidence} />
            </article>
          ))}
        </div>
      )}
    </Section>
  )
}

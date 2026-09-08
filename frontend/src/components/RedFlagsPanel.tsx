import type { RedFlag } from '../types'
import { EmptyState, Section } from './ui'

export function RedFlagsPanel({ flags }: { flags: RedFlag[] }) {
  return (
    <Section title="Red flags" eyebrow="Section 11 · Urgent clinical attention">
      {flags.length === 0 ? (
        <EmptyState message="No red flags identified for the selected medication(s) and available patient information." />
      ) : (
        <div className="space-y-3">
          {flags.map((f, idx) => (
            <article key={idx} className="border-l-4 border-signal-critical bg-signal-critical/5 p-4">
              <h3 className="font-display text-base text-signal-critical mb-2">{f.trigger}</h3>
              <dl className="text-sm space-y-1.5">
                <div>
                  <dt className="inline text-ink-500">Potential consequence: </dt>
                  <dd className="inline">{f.consequence}</dd>
                </div>
                <div>
                  <dt className="inline text-ink-500">Immediate consideration: </dt>
                  <dd className="inline">{f.immediate_consideration}</dd>
                </div>
                <div>
                  <dt className="inline text-ink-500">Recommended escalation: </dt>
                  <dd className="inline font-medium">{f.escalation}</dd>
                </div>
              </dl>
            </article>
          ))}
        </div>
      )}
    </Section>
  )
}

import type { Evidence } from '../types'
import { Section } from './ui'

const CONFIDENCE_STYLE: Record<string, string> = {
  High: 'text-signal-low',
  Moderate: 'text-signal-moderate',
  Limited: 'text-signal-high',
  Unknown: 'text-ink-500',
}

export function EvidencePanel({ evidence }: { evidence: Evidence[] }) {
  return (
    <Section title="Evidence and references" eyebrow="Section 15">
      <ul className="space-y-2 text-sm">
        {evidence.map((e, idx) => (
          <li key={idx} className="border-b rule pb-2">
            <p>
              <span className="font-medium">Source:</span> {e.source}
            </p>
            {e.reference && <p className="text-ink-500">Reference: {e.reference}</p>}
            {e.date && <p className="text-ink-500">Evidence date: {e.date}</p>}
            <p className={`font-medium ${CONFIDENCE_STYLE[e.confidence] ?? 'text-ink-500'}`}>
              Evidence confidence: {e.confidence}
            </p>
          </li>
        ))}
      </ul>
    </Section>
  )
}

export function MonitoringSchedulePanel({ schedule }: { schedule: Record<string, string[]> }) {
  const sections: { key: string; title: string }[] = [
    { key: 'before_treatment', title: 'Before treatment' },
    { key: 'early_treatment', title: 'Early treatment' },
    { key: 'ongoing', title: 'Ongoing' },
  ]
  return (
    <Section title="Monitoring schedule" eyebrow="Section 14">
      <div className="grid sm:grid-cols-3 gap-4">
        {sections.map((s) => (
          <div key={s.key} className="border border-ink-100 p-3">
            <p className="font-medium text-sm mb-2">{s.title}</p>
            <ul className="text-sm text-ink-700 space-y-1 list-disc list-inside">
              {(schedule[s.key] ?? []).map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </Section>
  )
}

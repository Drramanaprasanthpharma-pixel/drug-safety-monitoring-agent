import type { ReactNode } from 'react'
import type { Evidence, SeverityLevel } from '../types'

const SEVERITY_STYLES: Record<string, string> = {
  Critical: 'bg-signal-critical/10 text-signal-critical border-signal-critical/30',
  High: 'bg-signal-high/10 text-signal-high border-signal-high/30',
  Moderate: 'bg-signal-moderate/10 text-signal-moderate border-signal-moderate/30',
  Low: 'bg-signal-low/10 text-signal-low border-signal-low/30',
  Contraindicated: 'bg-signal-critical/10 text-signal-critical border-signal-critical/30',
  Major: 'bg-signal-high/10 text-signal-high border-signal-high/30',
  Minor: 'bg-signal-low/10 text-signal-low border-signal-low/30',
  Unknown: 'bg-ink-100 text-ink-500 border-ink-300',
}

export function SeverityBadge({ level }: { level: SeverityLevel | string }) {
  const style = SEVERITY_STYLES[level] ?? SEVERITY_STYLES.Unknown
  return (
    <span className={`inline-flex items-center rounded-sm border px-2 py-0.5 text-xs font-medium font-data ${style}`}>
      {level}
    </span>
  )
}

export function severityBarColor(level: string): string {
  switch (level) {
    case 'Critical':
      return '#8C1D18'
    case 'High':
      return '#B3261E'
    case 'Moderate':
      return '#B7791F'
    default:
      return '#3F7D45'
  }
}

export function Section({
  title,
  eyebrow,
  children,
  id,
}: {
  title: string
  eyebrow?: string
  children: ReactNode
  id?: string
}) {
  return (
    <section id={id} className="border-t rule pt-8 mt-8 first:mt-0 first:border-t-0 first:pt-0">
      <div className="mb-4">
        {eyebrow && <p className="text-sm text-teal-600 font-medium mb-1">{eyebrow}</p>}
        <h2 className="font-display text-2xl text-ink-950">{title}</h2>
      </div>
      {children}
    </section>
  )
}

export function EvidenceLine({ evidence }: { evidence?: Evidence | null }) {
  if (!evidence) return null
  return (
    <p className="text-xs text-ink-500 mt-1">
      <span className="font-medium">Source:</span> {evidence.source}
      {evidence.reference ? ` — ${evidence.reference}` : ''}
      {' · '}
      <span className="font-medium">Evidence confidence:</span> {evidence.confidence}
    </p>
  )
}

export function EmptyState({ message }: { message: string }) {
  return <p className="text-sm text-ink-500 italic py-4">{message}</p>
}

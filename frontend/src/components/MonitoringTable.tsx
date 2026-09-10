import type { MonitoringRow, VitalSignRow } from '../types'
import { EmptyState, Section, SeverityBadge } from './ui'

export function MonitoringTable({ rows }: { rows: MonitoringRow[] }) {
  return (
    <Section title="Monitoring parameters" eyebrow="Section 6">
      {rows.length === 0 ? (
        <EmptyState message="No specific laboratory monitoring parameters were identified." />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="text-left border-b-2 border-ink-950">
                <th className="py-2 pr-4 font-medium">Parameter</th>
                <th className="py-2 pr-4 font-medium">Why monitor?</th>
                <th className="py-2 pr-4 font-medium">Baseline</th>
                <th className="py-2 pr-4 font-medium">Follow-up</th>
                <th className="py-2 pr-4 font-medium">Alert threshold</th>
                <th className="py-2 pr-4 font-medium">Risk</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.parameter} className="border-b rule align-top">
                  <td className="py-3 pr-4 font-data font-medium whitespace-nowrap">{r.parameter}</td>
                  <td className="py-3 pr-4 text-ink-700 max-w-xs">{r.why}</td>
                  <td className="py-3 pr-4 text-ink-700">{r.baseline}</td>
                  <td className="py-3 pr-4 text-ink-700 max-w-xs">{r.follow_up}</td>
                  <td className="py-3 pr-4 text-ink-700 max-w-xs">{r.alert_threshold}</td>
                  <td className="py-3 pr-4">
                    <SeverityBadge level={r.risk} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Section>
  )
}

export function VitalSignsPanel({ rows }: { rows: VitalSignRow[] }) {
  if (rows.length === 0) return null
  return (
    <Section title="Vital sign monitoring" eyebrow="Section 7">
      <ul className="grid sm:grid-cols-2 gap-3">
        {rows.map((r) => (
          <li key={r.parameter} className="border border-ink-100 p-3 text-sm">
            <p className="font-medium">{r.parameter}</p>
            <p className="text-ink-700">{r.why}</p>
          </li>
        ))}
      </ul>
    </Section>
  )
}

import { useState } from 'react'
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { PriorityOrgan } from '../types'
import { EmptyState, EvidenceLine, Section, SeverityBadge, severityBarColor } from './ui'

export function OrganPriorityPanel({ organs }: { organs: PriorityOrgan[] }) {
  const [expanded, setExpanded] = useState<string | null>(organs[0]?.organ ?? null)

  if (organs.length === 0) {
    return (
      <Section title="Organ toxicity prioritization" eyebrow="Section 4–5">
        <EmptyState message="No organ-specific toxicity was identified for the selected medication(s)." />
      </Section>
    )
  }

  const chartData = organs.map((o) => ({ name: o.organ, percent: o.relative_priority_percent, priority: o.priority }))

  return (
    <Section title="Organ toxicity prioritization" eyebrow="Section 4–5">
      <p className="text-sm text-ink-500 mb-4">
        Relative monitoring priority generated from identified safety factors — not an incidence rate.
      </p>

      <div className="h-64 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 24 }}>
            <CartesianGrid horizontal={false} stroke="#E4E9EC" />
            <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 12, fill: '#5A7085' }} />
            <YAxis type="category" dataKey="name" width={110} tick={{ fontSize: 12, fill: '#152437' }} />
            <Tooltip
              formatter={(value: number) => [`${value}%`, 'Relative priority']}
              contentStyle={{ fontSize: 12, borderRadius: 2, borderColor: '#E4E9EC' }}
            />
            <Bar dataKey="percent" radius={[0, 2, 2, 0]}>
              {chartData.map((entry) => (
                <Cell key={entry.name} fill={severityBarColor(entry.priority)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <ol className="divide-y rule border-t border-b rule">
        {organs.map((o, idx) => {
          const isOpen = expanded === o.organ
          return (
            <li key={o.organ}>
              <button
                type="button"
                onClick={() => setExpanded(isOpen ? null : o.organ)}
                className="w-full flex items-center justify-between gap-4 py-3 text-left"
              >
                <span className="flex items-center gap-3">
                  <span className="font-data text-sm text-ink-500 w-5">{idx + 1}.</span>
                  <span className="font-display text-lg">{o.organ}</span>
                  <SeverityBadge level={o.priority} />
                </span>
                <span className="text-sm text-ink-500">{isOpen ? 'Hide detail' : 'Show detail'}</span>
              </button>
              {isOpen && (
                <div className="pb-4 pl-8 text-sm text-ink-700 space-y-2">
                  <p>
                    <span className="font-medium">Why flagged: </span>
                    {o.reason}
                  </p>
                  {o.toxicity && (
                    <p>
                      <span className="font-medium">Relevant toxicity: </span>
                      {o.toxicity}
                    </p>
                  )}
                  {o.monitoring_parameters.length > 0 && (
                    <p>
                      <span className="font-medium">Monitoring parameters: </span>
                      {o.monitoring_parameters.join(', ')}
                    </p>
                  )}
                  <p>
                    <span className="font-medium">Suggested frequency: </span>
                    {o.monitoring_frequency}
                  </p>
                  {o.intervention_threshold && (
                    <p>
                      <span className="font-medium">Intervention threshold: </span>
                      {o.intervention_threshold}
                    </p>
                  )}
                  <EvidenceLine evidence={o.evidence} />
                </div>
              )}
            </li>
          )
        })}
      </ol>
    </Section>
  )
}

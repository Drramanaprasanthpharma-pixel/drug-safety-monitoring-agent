import type { DashboardCards as DashboardCardsType } from '../types'
import { SeverityBadge } from './ui'

export function DashboardCards({ data }: { data: DashboardCardsType }) {
  const cards = [
    { label: 'Overall Safety', value: <SeverityBadge level={data.overall_risk_category} /> },
    {
      label: 'Priority Organ',
      value: (
        <span className="flex items-center gap-2">
          <span className="font-display text-lg">{data.priority_organ}</span>
          <SeverityBadge level={data.priority_organ_level} />
        </span>
      ),
    },
    { label: 'Drug Interactions', value: <span className="font-display text-2xl">{data.interaction_count}</span>, suffix: 'detected' },
    { label: 'Monitoring Parameters', value: <span className="font-display text-2xl">{data.monitoring_param_count}</span>, suffix: 'required' },
    { label: 'Red Flags', value: <span className="font-display text-2xl text-signal-high">{data.red_flag_count}</span>, suffix: 'detected' },
    { label: 'Patient Risk Factors', value: <span className="font-display text-2xl">{data.patient_risk_factor_count}</span>, suffix: 'identified' },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-px bg-ink-100 border border-ink-100">
      {cards.map((c) => (
        <div key={c.label} className="bg-white p-4">
          <p className="text-sm text-ink-500 mb-2">{c.label}</p>
          <div className="flex items-baseline gap-1.5">
            {c.value}
            {c.suffix && <span className="text-xs text-ink-500">{c.suffix}</span>}
          </div>
        </div>
      ))}
    </div>
  )
}

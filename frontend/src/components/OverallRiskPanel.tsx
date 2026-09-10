import type { OverallRisk } from '../types'
import { severityBarColor } from './ui'

export function OverallRiskPanel({ risk }: { risk: OverallRisk }) {
  const color = severityBarColor(risk.category)
  return (
    <div className="border border-ink-100 bg-white p-6">
      <div className="flex flex-col sm:flex-row sm:items-end gap-6">
        <div>
          <p className="text-sm text-ink-500 mb-1">Overall risk score</p>
          <p className="font-display text-5xl leading-none" style={{ color }}>
            {risk.priority_score}
            <span className="text-xl text-ink-500"> / 100</span>
          </p>
          <p className="mt-2 text-base font-medium" style={{ color }}>
            {risk.category}
          </p>
        </div>
        <div className="flex-1 min-w-0">
          <div className="h-2 w-full bg-ink-100 rounded-sm overflow-hidden mb-3">
            <div className="h-full rounded-sm" style={{ width: `${risk.priority_score}%`, backgroundColor: color }} />
          </div>
          <p className="text-sm text-ink-700">{risk.explanation}</p>
        </div>
      </div>
      <p className="mt-4 pt-4 border-t rule text-xs text-ink-500">
        {!risk.is_validated_score && (
          <>
            <span className="font-medium text-ink-700">{risk.score_label}.</span>{' '}
          </>
        )}
        This score is generated from the structured findings below (organ toxicity, interactions, red flags,
        and patient risk factors) and does not represent a validated clinical probability of harm.
      </p>
    </div>
  )
}

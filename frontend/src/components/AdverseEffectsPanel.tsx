import type { AdverseEffects } from '../types'
import { Section } from './ui'

export function AdverseEffectsPanel({ effects }: { effects: AdverseEffects[] }) {
  return (
    <Section title="Adverse drug reactions" eyebrow="Section 10">
      <div className="space-y-6">
        {effects.map((ae) => (
          <div key={ae.drug}>
            <h3 className="font-display text-lg mb-2">{ae.drug}</h3>
            {ae.boxed_warning && (
              <p className="text-sm border border-signal-critical/30 bg-signal-critical/5 text-signal-critical px-3 py-2 mb-3">
                <span className="font-semibold">Boxed warning: </span>
                {ae.boxed_warning}
              </p>
            )}
            <div className="grid sm:grid-cols-3 gap-4 text-sm">
              <EffectColumn label="Common" items={ae.common} tone="text-ink-700" />
              <EffectColumn label="Serious" items={ae.serious} tone="text-signal-moderate" />
              <EffectColumn label="Life-threatening" items={ae.life_threatening} tone="text-signal-critical" />
            </div>
          </div>
        ))}
      </div>
    </Section>
  )
}

function EffectColumn({ label, items, tone }: { label: string; items: string[]; tone: string }) {
  return (
    <div>
      <p className={`font-medium mb-1 ${tone}`}>{label}</p>
      {items.length === 0 ? (
        <p className="text-ink-500 italic">None documented</p>
      ) : (
        <ul className="list-disc list-inside space-y-0.5 text-ink-700">
          {items.map((i) => (
            <li key={i}>{i}</li>
          ))}
        </ul>
      )}
    </div>
  )
}

import { useState } from 'react'
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { LabTrendAssessment, LabTrendPoint } from '../types'
import { analyzeLabTrend } from '../api'
import { Section } from './ui'

export function LabTrendPanel() {
  const [parameter, setParameter] = useState('Creatinine')
  const [points, setPoints] = useState<LabTrendPoint[]>([
    { day: 0, value: 0.9 },
    { day: 7, value: 1.1 },
    { day: 14, value: 1.4 },
    { day: 21, value: 1.8 },
  ])
  const [day, setDay] = useState('')
  const [value, setValue] = useState('')
  const [assessment, setAssessment] = useState<LabTrendAssessment | null>(null)
  const [loading, setLoading] = useState(false)

  function addPoint() {
    if (day === '' || value === '') return
    setPoints([...points, { day: Number(day), value: Number(value) }].sort((a, b) => a.day - b.day))
    setDay('')
    setValue('')
    setAssessment(null)
  }

  function removePoint(idx: number) {
    setPoints(points.filter((_, i) => i !== idx))
    setAssessment(null)
  }

  async function runAssessment() {
    setLoading(true)
    try {
      setAssessment(await analyzeLabTrend(parameter, points))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Section title="Laboratory trend graphs" eyebrow="Section 12">
      <p className="text-sm text-ink-500 mb-4">
        Enter serial values for a lab parameter to visualize the trend. The system flags direction and
        magnitude of change only — it does not diagnose toxicity from a graph alone.
      </p>

      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-ink-700 mb-1.5" htmlFor="lab-param">
            Parameter
          </label>
          <input
            id="lab-param"
            type="text"
            value={parameter}
            onChange={(e) => setParameter(e.target.value)}
            className="input mb-3"
          />
          <div className="flex gap-2 mb-3">
            <input
              type="number"
              placeholder="Day"
              value={day}
              onChange={(e) => setDay(e.target.value)}
              className="input w-24"
            />
            <input
              type="number"
              step="0.01"
              placeholder="Value"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              className="input flex-1"
            />
            <button
              type="button"
              onClick={addPoint}
              className="px-3 py-1.5 text-sm font-medium text-teal-700 border border-teal-600 hover:bg-teal-100"
            >
              Add point
            </button>
          </div>
          <ul className="flex flex-wrap gap-2 mb-4">
            {points.map((p, idx) => (
              <li key={idx} className="font-data text-xs bg-ink-100 px-2 py-1 flex items-center gap-1.5">
                Day {p.day}: {p.value}
                <button type="button" onClick={() => removePoint(idx)} className="text-ink-500 hover:text-signal-high">
                  ×
                </button>
              </li>
            ))}
          </ul>
          <button
            type="button"
            onClick={runAssessment}
            disabled={points.length < 2 || loading}
            className="px-4 py-2 text-sm font-medium bg-ink-950 text-white disabled:opacity-40"
          >
            {loading ? 'Analyzing…' : 'Assess trend'}
          </button>

          {assessment && (
            <div className="mt-4 border border-ink-100 p-3 text-sm">
              <p>
                <span className="font-medium">Trend: </span>
                {assessment.trend}
              </p>
              <p className={assessment.clinically_significant_change ? 'text-signal-high font-medium' : 'text-ink-700'}>
                {assessment.note}
              </p>
            </div>
          )}
        </div>

        <div className="h-56 md:h-auto">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={points} margin={{ left: 0, right: 16, top: 8 }}>
              <CartesianGrid stroke="#E4E9EC" />
              <XAxis dataKey="day" tick={{ fontSize: 12, fill: '#5A7085' }} label={{ value: 'Day', position: 'insideBottom', offset: -5, fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12, fill: '#5A7085' }} domain={['auto', 'auto']} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 2, borderColor: '#E4E9EC' }} />
              <Line type="monotone" dataKey="value" stroke="#2B6E6E" strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </Section>
  )
}

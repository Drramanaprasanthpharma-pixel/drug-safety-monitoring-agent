import { useEffect, useRef, useState } from 'react'
import { searchDrugs } from '../api'
import type { DrugSummary } from '../types'

export function DrugSearch({
  selected,
  onChange,
}: {
  selected: DrugSummary[]
  onChange: (drugs: DrugSummary[]) => void
}) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<DrugSummary[]>([])
  const [open, setOpen] = useState(false)
  const boxRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handler = setTimeout(() => {
      if (query.trim().length === 0) {
        setResults([])
        return
      }
      searchDrugs(query)
        .then((r) => setResults(r.filter((d) => !selected.some((s) => s.id === d.id))))
        .catch(() => setResults([]))
    }, 150)
    return () => clearTimeout(handler)
  }, [query, selected])

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', onClickOutside)
    return () => document.removeEventListener('mousedown', onClickOutside)
  }, [])

  function addDrug(drug: DrugSummary) {
    onChange([...selected, drug])
    setQuery('')
    setResults([])
    setOpen(false)
  }

  function removeDrug(id: string) {
    onChange(selected.filter((d) => d.id !== id))
  }

  return (
    <div ref={boxRef} className="relative">
      <label htmlFor="drug-search" className="block text-sm font-medium text-ink-700 mb-1.5">
        Enter medication
      </label>
      <input
        id="drug-search"
        type="text"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value)
          setOpen(true)
        }}
        onFocus={() => setOpen(true)}
        placeholder="Generic or brand name — e.g. Warfarin or Coumadin"
        className="w-full border border-ink-300 bg-white px-3 py-2.5 text-base rounded-sm focus:border-teal-600 focus:ring-1 focus:ring-teal-600 outline-none"
        autoComplete="off"
      />
      {open && results.length > 0 && (
        <ul className="absolute z-20 mt-1 w-full bg-white border border-ink-300 rounded-sm shadow-lg max-h-64 overflow-auto">
          {results.map((d) => (
            <li key={d.id}>
              <button
                type="button"
                onClick={() => addDrug(d)}
                className="w-full text-left px-3 py-2 hover:bg-teal-100 flex items-baseline justify-between gap-2"
              >
                <span>
                  <span className="font-medium">{d.generic_name}</span>
                  {d.brand_names.length > 0 && (
                    <span className="text-ink-500 text-sm"> ({d.brand_names.join(', ')})</span>
                  )}
                </span>
                <span className="text-xs text-ink-500 whitespace-nowrap">{d.drug_class}</span>
              </button>
            </li>
          ))}
        </ul>
      )}

      {selected.length > 0 && (
        <ul className="flex flex-wrap gap-2 mt-3">
          {selected.map((d) => (
            <li
              key={d.id}
              className="inline-flex items-center gap-2 bg-teal-100 text-teal-700 border border-teal-500/30 rounded-sm px-2.5 py-1 text-sm font-medium"
            >
              {d.generic_name}
              <button
                type="button"
                onClick={() => removeDrug(d.id)}
                aria-label={`Remove ${d.generic_name}`}
                className="text-teal-700 hover:text-signal-high leading-none"
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

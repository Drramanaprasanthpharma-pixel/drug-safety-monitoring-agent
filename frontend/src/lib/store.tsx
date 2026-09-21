import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import type { AnalysisRequest, AnalysisResponse, PatientInfo } from "../types";

export interface PickedDrug { key: string; label: string; id?: string }

/** Hand-off from other pages into the review form. */
export interface ReviewDraft { drugs: PickedDrug[]; patient?: PatientInfo | null; demo?: boolean; autoRun?: boolean }

export interface LastReview { request: AnalysisRequest; result: AnalysisResponse; at: number }

interface Store {
  lastReview: LastReview | null;
  setLastReview: (r: LastReview | null) => void;
  draft: ReviewDraft | null;
  setDraft: (d: ReviewDraft | null) => void;
}

const Ctx = createContext<Store | null>(null);

/** Session-only, in-memory state. Patient context is deliberately never written to localStorage/sessionStorage. */
export function StoreProvider({ children }: { children: ReactNode }) {
  const [lastReview, setLast] = useState<LastReview | null>(null);
  const [draft, setDraftState] = useState<ReviewDraft | null>(null);
  const setLastReview = useCallback((r: LastReview | null) => setLast(r), []);
  const setDraft = useCallback((d: ReviewDraft | null) => setDraftState(d), []);
  const value = useMemo(() => ({ lastReview, setLastReview, draft, setDraft }), [lastReview, setLastReview, draft, setDraft]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useStore(): Store {
  const v = useContext(Ctx);
  if (!v) throw new Error("useStore must be used inside <StoreProvider>");
  return v;
}

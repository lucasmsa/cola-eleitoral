import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import { DEFAULT_WEIGHTS } from '@/config/answers';
import type { ColaSlotId } from '@/config/election';
import type { ColaEntry } from '@/lib/cola';
import type { Answer, Answers, Importance, Weights } from '@/lib/score';

interface AnswersState {
  answers: Answers;
  weights: Weights;
  cola: Partial<Record<ColaSlotId, ColaEntry>>;
  cola2: Partial<Record<ColaSlotId, ColaEntry>>;
  setAnswer: (questionId: string, answer: Answer) => void;
  setImportance: (questionId: string, importance: Importance) => void;
  setRecordWeight: (record: number) => void;
  setCola: (slot: ColaSlotId, entry: ColaEntry | null) => void;
  setCola2: (slot: ColaSlotId, entry: ColaEntry | null) => void;
  resetAll: () => void;
}

function safeStorage() {
  try {
    const probe = '__cola_probe__';
    window.localStorage.setItem(probe, probe);
    window.localStorage.removeItem(probe);
    return window.localStorage;
  } catch {
    const memory = new Map<string, string>();
    return {
      getItem: (k: string) => memory.get(k) ?? null,
      setItem: (k: string, v: string) => void memory.set(k, v),
      removeItem: (k: string) => void memory.delete(k),
    };
  }
}

export const useAnswersStore = create<AnswersState>()(
  persist(
    (set) => ({
      answers: {},
      weights: DEFAULT_WEIGHTS,
      cola: {},
      cola2: {},
      setAnswer: (questionId, answer) => set((s) => ({ answers: { ...s.answers, [questionId]: answer } })),
      setImportance: (questionId, importance) =>
        set((s) => {
          const current = s.answers[questionId];
          if (!current || current === 'skip') return s;
          return { answers: { ...s.answers, [questionId]: { ...current, importance } } };
        }),
      setRecordWeight: (record) => {
        const r = Math.min(1, Math.max(0, Math.round(record * 100) / 100));
        set({ weights: { record: r, platform: Math.round((1 - r) * 100) / 100 } });
      },
      setCola: (slot, entry) =>
        set((s) => {
          const cola = { ...s.cola };
          if (entry) cola[slot] = entry;
          else delete cola[slot];
          return { cola };
        }),
      setCola2: (slot, entry) =>
        set((s) => {
          const cola2 = { ...s.cola2 };
          if (entry) cola2[slot] = entry;
          else delete cola2[slot];
          return { cola2 };
        }),
      resetAll: () => set({ answers: {}, weights: DEFAULT_WEIGHTS, cola: {}, cola2: {} }),
    }),
    { name: 'cola-eleitoral:v1', storage: createJSONStorage(safeStorage) },
  ),
);

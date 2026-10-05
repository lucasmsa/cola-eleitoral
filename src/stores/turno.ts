import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';

export type Turno = 1 | 2;

interface TurnoState {
  turno: Turno;
  setTurno: (turno: Turno) => void;
}

function safeStorage() {
  try {
    window.localStorage.setItem('__turno_probe__', '1');
    window.localStorage.removeItem('__turno_probe__');
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

export const useTurnoStore = create<TurnoState>()(
  persist((set) => ({ turno: 2, setTurno: (turno) => set({ turno }) }), {
    name: 'cola-eleitoral:turno',
    storage: createJSONStorage(safeStorage),
  }),
);

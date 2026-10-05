import { create } from 'zustand';
import type { ResultStep } from '@/config/result';

export type Screen =
  | { name: 'home' }
  | { name: 'lesson'; unitId: string }
  | { name: 'results'; step: ResultStep }
  | { name: 'review' }
  | { name: 'cola' }
  | { name: 'round2' }
  | { name: 'round1' }
  | { name: 'cola2' };

interface ScreenState {
  screen: Screen;
  go: (screen: Screen) => void;
}

export const useScreenStore = create<ScreenState>((set) => ({
  screen: { name: 'home' },
  go: (screen) => {
    set({ screen });
    if (typeof window !== 'undefined' && typeof window.scrollTo === 'function') {
      try {
        window.scrollTo({ top: 0 });
      } catch {
        /* jsdom */
      }
    }
  },
}));

import { useMemo, useState } from 'react';
import { candidates, evidence, portraits, profiles, questions } from '@/data';
import { indexPortraits } from '@/lib/portraits';
import { generateReview, type ReviewCard } from '@/lib/review';
import { buildCatalog, describeSubject } from '@/lib/subjects';
import { useNav } from './useNav';

const catalog = buildCatalog(candidates);
const portraitIndex = indexPortraits(portraits);
export const REVIEW_LENGTH = 10;

export type ReviewPhase = 'intro' | 'card' | 'done' | 'mistakes';

export function useReview() {
  const nav = useNav();
  const [seed, setSeed] = useState(() => Math.floor(Math.random() * 1_000_000));
  const cards = useMemo(() => generateReview({ evidence, catalog, profiles, questions, seed, limit: REVIEW_LENGTH }), [seed]);
  const [phase, setPhase] = useState<ReviewPhase>('intro');
  const [index, setIndex] = useState(0);
  const [picked, setPicked] = useState<number | null>(null);
  const [mistakes, setMistakes] = useState<{ card: ReviewCard; picked: number }[]>([]);
  const card = cards[index] ?? null;

  function pick(option: number) {
    if (picked !== null || !card) return;
    setPicked(option);
    if (option !== card.correct) setMistakes((m) => [...m, { card, picked: option }]);
  }

  function next() {
    setPicked(null);
    if (index + 1 >= cards.length) {
      setPhase('done');
      return;
    }
    setIndex((i) => i + 1);
  }

  function again() {
    setSeed((s) => s + 1);
    setIndex(0);
    setPicked(null);
    setMistakes([]);
    setPhase('card');
  }

  return {
    phase,
    card,
    position: Math.min(index + 1, cards.length),
    total: cards.length,
    progress: cards.length === 0 ? 0 : (index + (picked === null ? 0 : 1)) / cards.length,
    picked,
    correct: picked !== null && card ? picked === card.correct : null,
    hits: cards.length - mistakes.length,
    mistakes,
    nameOf: (id: string | null) => (id ? describeSubject(catalog, { type: 'candidate', id }).name : ''),
    portraitOf: (id: string | null) => (id ? (portraitIndex.get(id)?.file ?? null) : null),
    start: () => setPhase('card'),
    pick,
    next,
    again,
    showMistakes: () => setPhase('mistakes'),
    backToScore: () => setPhase('done'),
    exit: nav.goHome,
    goCola: nav.goCola,
  };
}

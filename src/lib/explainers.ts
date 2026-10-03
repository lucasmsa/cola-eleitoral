import type { Claim, Explainer } from '@/data/schema';

export type ExplainerSectionKey = 'whatItIs' | 'inPractice' | 'argsFor' | 'argsAgainst' | 'nuance';

export interface ExplainerSection {
  key: ExplainerSectionKey;
  title: string;
  claims: Claim[];
}

export const EXPLAINER_SECTIONS: { key: ExplainerSectionKey; title: string }[] = [
  { key: 'whatItIs', title: 'O que é' },
  { key: 'inPractice', title: 'Na prática' },
  { key: 'argsFor', title: 'Quem defende argumenta' },
  { key: 'argsAgainst', title: 'Quem critica argumenta' },
  { key: 'nuance', title: 'Nuances' },
];

export function explainerFor(explainers: Explainer[], questionId: string): Explainer | null {
  return explainers.find((e) => e.questionId === questionId) ?? null;
}

export function explainerSections(explainer: Explainer | null): ExplainerSection[] {
  if (!explainer) return [];
  return EXPLAINER_SECTIONS.map((s) => ({ ...s, claims: explainer[s.key] ?? [] })).filter((s) => s.claims.length > 0);
}

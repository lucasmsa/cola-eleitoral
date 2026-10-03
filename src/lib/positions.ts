export type PositionTone = 'favor' | 'contra' | 'meio';

export function positionTone(position: number): PositionTone {
  if (position > 0.33) return 'favor';
  if (position < -0.33) return 'contra';
  return 'meio';
}

export const POSITION_LABEL: Record<PositionTone, string> = {
  favor: 'A favor',
  contra: 'Contra',
  meio: 'Meio-termo',
};

export function stanceLabel(stance: number): string {
  if (stance <= -1) return 'Discordo totalmente';
  if (stance < 0) return 'Discordo';
  if (stance === 0) return 'Neutro';
  if (stance < 1) return 'Concordo';
  return 'Concordo totalmente';
}

export interface StanceOption {
  value: -1 | -0.5 | 0 | 0.5 | 1;
  label: string;
}

/** A question's own labelled scale when it has one, otherwise the five generic stances; always ordered from -1 to 1. */
export function stanceOptionsFor(question: { options?: StanceOption[] }, generic: StanceOption[]): StanceOption[] {
  const own = question.options?.filter((o) => o.label.trim().length > 0) ?? [];
  if (own.length < 2) return generic;
  return [...own].sort((a, b) => a.value - b.value);
}

export function answerLabel(question: { options?: StanceOption[] } | undefined, stance: number): string {
  const own = question?.options?.find((o) => o.value === stance);
  return own ? own.label : stanceLabel(stance);
}

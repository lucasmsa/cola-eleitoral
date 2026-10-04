import type { AxisAssignment, CountryStance, Evidence } from '@/data/schema';
import { blendPosition, type Answers, type Weights } from './score';

/**
 * Axis convention: on `economico`, +1 is "mais mercado" and -1 "mais Estado";
 * on `social`, +1 is "conservador" and -1 "progressista". An assignment's
 * `direction` says which pole "concordo" with the question points to.
 */
export const MIN_PER_AXIS = 2;
/** Neutral pseudo-answers added to every axis so few positions cannot reach the edge. */
export const AXIS_SHRINK = 2;
export const MIN_COMMON = 3;

export type PositionMap = Map<string, number>;

export interface AxisPoint {
  value: number;
  n: number;
}

export interface Placement {
  x: AxisPoint;
  y: AxisPoint;
  visible: boolean;
}

export interface Agreement {
  score: number | null;
  common: number;
}

export type EntityKind = 'politico' | 'partido' | 'pais';

export interface AlignedEntity {
  id: string;
  label: string;
  detail: string;
  kind: EntityKind;
  positions: PositionMap;
}

export function answerPositions(answers: Answers): PositionMap {
  const map: PositionMap = new Map();
  for (const [id, a] of Object.entries(answers)) if (a !== 'skip') map.set(id, a.stance);
  return map;
}

export function subjectPositions(evidence: Evidence[], subject: Evidence['subject'], weights: Weights): PositionMap {
  const byQuestion = new Map<string, Evidence[]>();
  for (const e of evidence) {
    if (e.subject.type !== subject.type || e.subject.id !== subject.id) continue;
    byQuestion.set(e.questionId, [...(byQuestion.get(e.questionId) ?? []), e]);
  }
  const map: PositionMap = new Map();
  for (const [q, items] of byQuestion) {
    const blended = blendPosition(items, weights);
    if (blended) map.set(q, blended.position);
  }
  return map;
}

export function countryPositions(stances: CountryStance[], country: string): PositionMap {
  const byQuestion = new Map<string, number[]>();
  for (const s of stances) {
    if (s.country !== country) continue;
    byQuestion.set(s.questionId, [...(byQuestion.get(s.questionId) ?? []), s.position]);
  }
  return new Map([...byQuestion].map(([q, ps]) => [q, ps.reduce((a, b) => a + b, 0) / ps.length]));
}

function axisPoint(positions: PositionMap, axes: AxisAssignment[]): AxisPoint {
  let sum = 0;
  let n = 0;
  for (const a of axes) {
    const p = positions.get(a.questionId);
    if (p === undefined) continue;
    sum += p * a.direction;
    n += 1;
  }
  return { value: sum / (n + AXIS_SHRINK), n };
}

export function placeOnAxes(positions: PositionMap, axes: AxisAssignment[]): Placement {
  const x = axisPoint(positions, axes.filter((a) => a.axis === 'economico'));
  const y = axisPoint(positions, axes.filter((a) => a.axis === 'social'));
  return { x, y, visible: x.n >= MIN_PER_AXIS && y.n >= MIN_PER_AXIS };
}

export function agreementWith(answers: Answers, positions: PositionMap): Agreement {
  let weight = 0;
  let agreed = 0;
  let common = 0;
  for (const [id, a] of Object.entries(answers)) {
    if (a === 'skip') continue;
    const p = positions.get(id);
    if (p === undefined) continue;
    common += 1;
    weight += a.importance;
    agreed += a.importance * (1 - Math.abs(a.stance - p) / 2);
  }
  return { score: weight === 0 ? null : agreed / weight, common };
}

export interface RankedEntity {
  entity: AlignedEntity;
  agreement: Agreement;
}

export function rankAligned(entities: AlignedEntity[], answers: Answers, minCommon = MIN_COMMON): RankedEntity[] {
  return entities
    .map((entity) => ({ entity, agreement: agreementWith(answers, entity.positions) }))
    .filter((r) => r.agreement.score !== null && r.agreement.common >= minCommon)
    .sort((a, b) => (b.agreement.score ?? 0) - (a.agreement.score ?? 0) || b.agreement.common - a.agreement.common);
}

/** Maps an axis value in [-1, 1] to a 0..1 fraction along the drawing. */
export function toUnit(value: number): number {
  return (Math.max(-1, Math.min(1, value)) + 1) / 2;
}

export function answersMissing(minPerAxis: number, have: { x: number; y: number }): { x: number; y: number } {
  return { x: Math.max(0, minPerAxis - have.x), y: Math.max(0, minPerAxis - have.y) };
}

import { AREAS, PB_UNIT_LABEL } from '@/config/election';
import type { Question } from '@/data/schema';
import type { Answers } from './score';

export interface Unit {
  id: string;
  label: string;
  blurb: string;
  questions: Question[];
}

const STATE_OFFICES = new Set(['governador', 'deputado_estadual']);

export function isStateQuestion(q: Question): boolean {
  return q.id.startsWith('pb-') || q.offices.every((o) => STATE_OFFICES.has(o));
}

export function buildUnits(questions: Question[]): Unit[] {
  const units: Unit[] = AREAS.map((area) => ({
    id: area.id,
    label: area.label,
    blurb: area.blurb,
    questions: questions.filter((q) => q.area === area.id && !isStateQuestion(q)),
  })).filter((u) => u.questions.length > 0);
  const pb = questions.filter(isStateQuestion);
  if (pb.length > 0) {
    units.push({
      id: 'pb',
      label: PB_UNIT_LABEL,
      blurb: 'Temas do governo do estado e da Assembleia Legislativa.',
      questions: pb,
    });
  }
  return units;
}

export function unitProgress(unit: Unit, answers: Answers): { answered: number; total: number } {
  const answered = unit.questions.filter((q) => answers[q.id] !== undefined).length;
  return { answered, total: unit.questions.length };
}

export function firstOpenIndex(unit: Unit, answers: Answers): number {
  const index = unit.questions.findIndex((q) => answers[q.id] === undefined);
  return index === -1 ? unit.questions.length : index;
}

export type UnitStatus = 'start' | 'resume' | 'redo';

export function unitStatus(answered: number, total: number): UnitStatus {
  if (answered === 0) return 'start';
  if (answered < total) return 'resume';
  return 'redo';
}

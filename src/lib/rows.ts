import type { Evidence } from '@/data/schema';
import { coveredCount, isThinEvidence, measuredLabel, type Ranking } from './results';
import type { Answers, SubjectScore } from './score';
import { describeSubject, type Catalog } from './subjects';

export interface ResultRow {
  type: 'candidate' | 'list';
  id: string;
  name: string;
  number: string | null;
  listName: string;
  score: SubjectScore;
  covered: number;
  answered: number;
  measured: string;
  thin: boolean;
  history: string | null;
  notice: string | null;
  portrait: string | null;
}

export function historyLine(catalog: Catalog, id: string): string | null {
  const last = catalog.candidates.get(id)?.elected[0];
  if (!last) return null;
  return `Eleito ${last.office.toLowerCase()} (${last.place}) em ${last.year}`;
}

export function buildRows(
  ranking: Ranking,
  type: 'candidate' | 'list',
  catalog: Catalog,
  answers: Answers,
  evidence: Evidence[],
  portraitOf: (id: string) => string | null = () => null,
): { scored: ResultRow[]; unscored: ResultRow[] } {
  const map = (s: SubjectScore): ResultRow => {
    const info = describeSubject(catalog, { type, id: s.subjectId });
    const covered = coveredCount({ type, id: s.subjectId }, answers, evidence);
    return {
      type,
      id: s.subjectId,
      name: info.name,
      number: info.number,
      listName: info.listName,
      score: s,
      covered,
      answered: ranking.answered,
      thin: isThinEvidence(covered, ranking.answered),
      measured: measuredLabel(s.measuredShare),
      history: type === 'candidate' ? historyLine(catalog, s.subjectId) : null,
      notice: type === 'candidate' ? (catalog.candidates.get(s.subjectId)?.notice?.text ?? null) : null,
      portrait: type === 'candidate' ? portraitOf(s.subjectId) : null,
    };
  };
  return { scored: ranking.scored.map(map), unscored: ranking.unscored.map(map) };
}

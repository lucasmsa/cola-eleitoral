import type { Candidate, Evidence, Office, Question } from '@/data/schema';
import { rankSubjects, type Answers, type SubjectScore, type Weights } from './score';

export function questionsForOffice(questions: Question[], office: Office): Question[] {
  return questions.filter((q) => q.offices.includes(office));
}

export function filterAnswers(answers: Answers, questions: Question[]): Answers {
  const ids = new Set(questions.map((q) => q.id));
  return Object.fromEntries(Object.entries(answers).filter(([id]) => ids.has(id)));
}

export function answeredCount(answers: Answers): number {
  return Object.values(answers).filter((a) => a !== 'skip').length;
}

export interface Ranking {
  scored: SubjectScore[];
  unscored: SubjectScore[];
  answered: number;
}

function split(scores: SubjectScore[], answered: number): Ranking {
  return {
    scored: scores.filter((s) => s.score !== null),
    unscored: scores.filter((s) => s.score === null),
    answered,
  };
}

export function rankCandidates(
  office: Office,
  candidates: Candidate[],
  questions: Question[],
  evidence: Evidence[],
  answers: Answers,
  weights: Weights,
  listId?: string,
): Ranking {
  const scoped = filterAnswers(answers, questionsForOffice(questions, office));
  const ids = candidates
    .filter((c) => c.office === office && !c.withdrawn && (listId === undefined || c.list === listId))
    .map((c) => c.id);
  return split(rankSubjects(ids, scoped, evidence, weights, 'candidate'), answeredCount(scoped));
}

export function listsForOffice(office: Office, candidates: Candidate[]): string[] {
  return [...new Set(candidates.filter((c) => c.office === office).map((c) => c.list))];
}

export function rankLists(
  office: Office,
  candidates: Candidate[],
  evidence: Evidence[],
  answers: Answers,
  weights: Weights,
): Ranking {
  const ids = listsForOffice(office, candidates);
  return split(rankSubjects(ids, answers, evidence, weights, 'list'), answeredCount(answers));
}

export function coveredCount(
  subject: { type: 'candidate' | 'list'; id: string },
  answers: Answers,
  evidence: Evidence[],
): number {
  const covered = new Set(
    evidence.filter((e) => e.subject.type === subject.type && e.subject.id === subject.id).map((e) => e.questionId),
  );
  return Object.entries(answers).filter(([id, a]) => a !== 'skip' && covered.has(id)).length;
}

export function measuredLabel(measuredShare: number): string {
  if (measuredShare >= 0.995) return 'medido';
  if (measuredShare <= 0.005) return 'declarado, não medido';
  return `${Math.round(measuredShare * 100)}% medido`;
}

const THIN_SHARE = 0.4;

export function isThinEvidence(covered: number, answered: number): boolean {
  return answered > 0 && covered / answered < THIN_SHARE;
}

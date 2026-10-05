import type { Candidate, Evidence, Office, Question, Round2, Round2Finalist } from '@/data/schema';
import { daysUntil } from './days';
import type { Unit } from './lessons';
import { filterAnswers, questionsForOffice } from './results';
import { blendPosition, scoreSubject, type Answers, type SubjectScore, type Weights } from './score';

export function finalistsOf(round2: Round2, office: Office): Round2Finalist[] {
  const entry = round2.offices.find((o) => o.office === office);
  return entry?.status === 'runoff' ? (entry.finalists ?? []) : [];
}

export function winnerOf(round2: Round2, office: Office) {
  const entry = round2.offices.find((o) => o.office === office);
  return entry?.status === 'decided' ? (entry.winner ?? null) : null;
}

export interface Side {
  position: number | null;
  evidence: Evidence[];
}

export interface HeadToHeadRow {
  question: Question;
  sides: Record<string, Side>;
}

export interface HeadToHead {
  finalists: Round2Finalist[];
  scores: Record<string, SubjectScore>;
  rows: HeadToHeadRow[];
  officeQuestionIds: string[];
}

function sideFor(candidateId: string, questionId: string, evidence: Evidence[], weights: Weights): Side {
  const own = evidence.filter((e) => e.subject.type === 'candidate' && e.subject.id === candidateId && e.questionId === questionId);
  return { position: blendPosition(own, weights)?.position ?? null, evidence: own };
}

function sidesWithEvidence(row: HeadToHeadRow): number {
  return Object.values(row.sides).filter((s) => s.position !== null).length;
}

export function headToHead(
  round2: Round2,
  office: Office,
  questions: Question[],
  evidence: Evidence[],
  answers: Answers,
  weights: Weights,
): HeadToHead {
  const finalists = finalistsOf(round2, office);
  const officeQuestions = questionsForOffice(questions, office);
  const scoped = filterAnswers(answers, officeQuestions);
  const scores = Object.fromEntries(
    finalists.map((f) => [f.candidateId, scoreSubject(f.candidateId, scoped, evidence, weights, 'candidate')]),
  );
  const rows = officeQuestions
    .map((question) => ({
      question,
      sides: Object.fromEntries(finalists.map((f) => [f.candidateId, sideFor(f.candidateId, question.id, evidence, weights)])),
    }))
    .filter((row) => sidesWithEvidence(row) > 0)
    .sort((a, b) => sidesWithEvidence(b) - sidesWithEvidence(a));
  return { finalists, scores, rows, officeQuestionIds: officeQuestions.map((qq) => qq.id) };
}

/** Relevant questions the user has neither answered nor skipped; questions both finalists took a side on come first. */
export function missingQuestions(h: HeadToHead, answers: Answers): Question[] {
  return h.rows.filter((r) => answers[r.question.id] === undefined).map((r) => r.question);
}

export function firstMissingUnit(units: Unit[], missing: Question[]): string | null {
  const first = missing[0];
  if (!first) return null;
  return units.find((u) => u.questions.some((qq) => qq.id === first.id))?.id ?? null;
}

export function round2Candidates(round2: Round2, candidates: Candidate[]): Candidate[] {
  const ids = round2.offices.flatMap((o) => (o.finalists ?? []).map((f) => f.candidateId));
  return ids.map((id) => candidates.find((c) => c.id === id)).filter((c): c is Candidate => Boolean(c));
}

export function activeElection(todayIso: string, round1: string, round2: string): { round: 1 | 2; date: string; days: number } {
  const daysToFirst = daysUntil(todayIso, round1);
  if (daysToFirst >= 0) return { round: 1, date: round1, days: daysToFirst };
  return { round: 2, date: round2, days: daysUntil(todayIso, round2) };
}

/** Same denominators as the score: answered = non-skipped answers on the office's questions. */
export function finalistCoverage(h: HeadToHead, answers: Answers, candidateId: string): { covered: number; answered: number } {
  const answered = h.officeQuestionIds.filter((id) => answers[id] !== undefined && answers[id] !== 'skip');
  const withPosition = new Set(h.rows.filter((r) => r.sides[candidateId]?.position !== null).map((r) => r.question.id));
  return { covered: answered.filter((id) => withPosition.has(id)).length, answered: answered.length };
}

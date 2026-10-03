import type { Evidence } from '@/data/schema';

export type Stance = -1 | -0.5 | 0 | 0.5 | 1;
export type Importance = 0.5 | 1 | 2;
export type Answer = { stance: Stance; importance: Importance } | 'skip';
export type Answers = Record<string, Answer>;
export type Weights = { record: number; platform: number };
export type SubjectType = 'candidate' | 'list';

export interface SubjectScore {
  subjectId: string;
  score: number | null;
  low: number;
  high: number;
  coverage: number;
  measuredShare: number;
}

function mean(values: number[]): number | null {
  if (values.length === 0) return null;
  return values.reduce((sum, v) => sum + v, 0) / values.length;
}

export function blendPosition(
  evidence: Evidence[],
  weights: Weights,
): { position: number; measured: boolean } | null {
  const record = mean(evidence.filter((e) => e.kind === 'record').map((e) => e.position));
  const platform = mean(evidence.filter((e) => e.kind === 'platform').map((e) => e.position));
  if (record === null && platform === null) return null;
  if (record === null) return { position: platform as number, measured: false };
  if (platform === null) return { position: record, measured: true };
  const total = weights.record + weights.platform;
  return { position: (record * weights.record + platform * weights.platform) / total, measured: true };
}

function agreement(stance: number, position: number): number {
  return 1 - Math.abs(stance - position) / 2;
}

export function scoreSubject(
  subjectId: string,
  answers: Answers,
  evidence: Evidence[],
  weights: Weights,
  subjectType: SubjectType = 'candidate',
): SubjectScore {
  const own = evidence.filter((e) => e.subject.type === subjectType && e.subject.id === subjectId);
  let answeredWeight = 0;
  let coveredWeight = 0;
  let measuredWeight = 0;
  let agreedWeight = 0;

  for (const [questionId, answer] of Object.entries(answers)) {
    if (answer === 'skip') continue;
    answeredWeight += answer.importance;
    const blended = blendPosition(
      own.filter((e) => e.questionId === questionId),
      weights,
    );
    if (!blended) continue;
    coveredWeight += answer.importance;
    if (blended.measured) measuredWeight += answer.importance;
    agreedWeight += answer.importance * agreement(answer.stance, blended.position);
  }

  if (coveredWeight === 0) {
    return { subjectId, score: null, low: 0, high: 1, coverage: 0, measuredShare: 0 };
  }

  const missingWeight = answeredWeight - coveredWeight;
  return {
    subjectId,
    score: agreedWeight / coveredWeight,
    low: agreedWeight / answeredWeight,
    high: (agreedWeight + missingWeight) / answeredWeight,
    coverage: coveredWeight / answeredWeight,
    measuredShare: measuredWeight / coveredWeight,
  };
}

function compareScores(a: SubjectScore, b: SubjectScore): number {
  if (a.score === null && b.score === null) return 0;
  if (a.score === null) return 1;
  if (b.score === null) return -1;
  return b.score - a.score || b.coverage - a.coverage;
}

export function rankSubjects(
  subjectIds: string[],
  answers: Answers,
  evidence: Evidence[],
  weights: Weights,
  subjectType: SubjectType = 'candidate',
): SubjectScore[] {
  return subjectIds
    .map((id) => scoreSubject(id, answers, evidence, weights, subjectType))
    .sort(compareScores);
}

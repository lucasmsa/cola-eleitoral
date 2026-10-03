import type { SubjectScore } from './score';

export function bandGeometry(score: SubjectScore): { left: string; width: string; point: string | null } {
  const low = Math.max(0, Math.min(1, score.low));
  const high = Math.max(low, Math.min(1, score.high));
  return {
    left: `${low * 100}%`,
    width: `${(high - low) * 100}%`,
    point: score.score === null ? null : `${score.score * 100}%`,
  };
}

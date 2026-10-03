import { bandGeometry } from '@/lib/band';
import type { SubjectScore } from '@/lib/score';

export function ScoreBand({ score }: { score: SubjectScore }) {
  const g = bandGeometry(score);
  return (
    <div className="relative h-5 w-full rounded-full border-2 border-edge bg-paper" aria-hidden="true">
      <div className="absolute inset-y-0 rounded-full bg-pen-soft" style={{ left: g.left, width: g.width }} />
      {g.point && (
        <div className="absolute -top-1 h-6 w-1.5 -translate-x-1/2 rounded-full bg-pen" style={{ left: g.point }} />
      )}
    </div>
  );
}

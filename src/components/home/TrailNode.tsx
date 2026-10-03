import { useTrailNode } from '@/hooks/useTrailNode';
import { CheckMark } from '../shell/icons';

export function TrailNode({ index, progress, done }: { index: number; progress: number; done: boolean }) {
  const { canvasRef, status } = useTrailNode(progress, done);
  return (
    <span className="relative grid size-16 shrink-0 place-items-center" aria-hidden="true">
      <canvas ref={canvasRef} width={128} height={128} className={`absolute inset-0 size-16 ${status === 'ready' ? 'visible' : 'invisible'}`} />
      {status !== 'ready' && (
        <span className={`grid size-14 place-items-center rounded-full border-2 text-2xl font-extrabold ${done ? 'border-ink bg-ink text-paper' : 'border-edge text-ink'}`}>
          {done ? <CheckMark className="size-7" /> : index}
        </span>
      )}
      {status === 'ready' && !done && <span className="relative text-2xl font-extrabold text-ink">{index}</span>}
    </span>
  );
}

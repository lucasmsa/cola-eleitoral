import type { Mood } from '@/config/mascot';
import { useMascot } from '@/hooks/useMascot';

export function Mascot({ mood, size, nodKey = 0 }: { mood: Mood; size: number; nodKey?: number }) {
  const { canvasRef, status } = useMascot(mood, nodKey);
  return (
    <span className="relative block shrink-0" style={{ width: size, height: size }} aria-hidden="true">
      {status === 'missing' && (
        <span className="block size-full rounded-full border-2 border-edge bg-favor-soft" />
      )}
      <canvas ref={canvasRef} width={size * 2} height={size * 2} style={{ width: size, height: size }} className={status === 'missing' ? 'hidden' : 'block'} />
    </span>
  );
}

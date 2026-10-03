import { motion } from 'motion/react';
import { COPY } from '@/config/copy';
import { STAMP } from '@/config/rive';
import { useStamp } from '@/hooks/useStamp';
import { Button } from '../shell/ui';

interface Props {
  skipped: boolean;
  last: boolean;
  onNext: () => void;
}

export function RecordedMoment({ skipped, last, onNext }: Props) {
  const { canvasRef, status } = useStamp(STAMP);
  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="grid justify-items-start gap-4"
      aria-live="polite"
    >
      <div className="relative h-32 w-56">
        <canvas ref={canvasRef} width={448} height={256} className={`size-full ${status === 'ready' ? 'block' : 'hidden'}`} aria-hidden="true" />
        {status !== 'ready' && (
          <motion.span
            initial={{ scale: 1.8, rotate: -14, opacity: 0 }}
            animate={{ scale: 1, rotate: -6, opacity: 1 }}
            transition={{ type: 'spring', stiffness: 420, damping: 18 }}
            className="absolute inset-0 grid place-items-center rounded-md border-4 border-pen font-hand text-4xl font-bold text-pen"
            aria-hidden="true"
          >
            {skipped ? COPY.lesson.stampSkip : COPY.lesson.stamp}
          </motion.span>
        )}
      </div>
      <p className="text-2xl font-bold">{skipped ? COPY.lesson.recordedSkip : COPY.lesson.recorded}</p>
      <p className="max-w-[55ch] text-lg text-muted">{COPY.lesson.recordedHint}</p>
      <Button variant="pen" onClick={onNext}>
        {last ? COPY.lesson.finish : COPY.lesson.nextQuestion}
      </Button>
    </motion.section>
  );
}

import { COPY } from '@/config/copy';
import { Mascot } from '../shell/Mascot';
import { Button, Hand } from '../shell/ui';

interface Props {
  unitLabel: string;
  nextUnitLabel: string | null;
  onNext: () => void;
  onResults: () => void;
  onHome: () => void;
  onRestart: () => void;
  onBack: () => void;
}

export function LessonDone({ unitLabel, nextUnitLabel, onNext, onResults, onHome, onRestart, onBack }: Props) {
  return (
    <main className="mx-auto grid max-w-2xl justify-items-center gap-6 px-4 py-12 text-center">
      <Mascot mood="happy" size={160} />
      <Hand className="text-4xl">{unitLabel}</Hand>
      <h1 className="text-5xl font-extrabold">{COPY.lesson.doneTitle}</h1>
      <p className="max-w-[48ch] text-xl text-muted">{COPY.lesson.doneBody}</p>
      <div className="flex flex-wrap justify-center gap-3">
        {nextUnitLabel && (
          <Button variant="pen" onClick={onNext}>
            {COPY.lesson.nextUnit}: {nextUnitLabel}
          </Button>
        )}
        <Button variant={nextUnitLabel ? 'ghost' : 'pen'} onClick={onResults}>
          {COPY.lesson.toResults}
        </Button>
        <Button variant="quiet" onClick={onHome}>
          {COPY.lesson.home}
        </Button>
        <Button variant="quiet" onClick={onBack}>
          {COPY.lesson.backToLast}
        </Button>
        <Button variant="quiet" onClick={onRestart}>
          {COPY.home.redo}
        </Button>
      </div>
    </main>
  );
}

import { AnimatePresence, motion } from 'motion/react';
import { COPY } from '@/config/copy';
import { IMPORTANCES, STANCES } from '@/config/answers';
import { useLesson } from '@/hooks/useLesson';
import { explainerSections } from '@/lib/explainers';
import { stanceOptionsFor } from '@/lib/positions';
import { Chevron, CloseMark } from '../shell/icons';
import { Mascot } from '../shell/Mascot';
import { Button, ProgressBar } from '../shell/ui';
import { ExplainerPanel } from './ExplainerPanel';
import { ImportanceChips } from './ImportanceChips';
import { LessonDone } from './LessonDone';
import { RecordedMoment } from './RecordedMoment';
import { StanceOptions } from './StanceOptions';

export function LessonScreen({ unitId }: { unitId: string }) {
  const lesson = useLesson(unitId);
  if (!lesson.unit || !lesson.question) return null;

  if (lesson.phase === 'done') {
    return (
      <LessonDone
        unitLabel={lesson.unit.label}
        nextUnitLabel={lesson.nextUnit?.label ?? null}
        onNext={lesson.openNextUnit}
        onResults={lesson.openResults}
        onHome={lesson.exit}
        onRestart={lesson.restart}
        onBack={lesson.back}
      />
    );
  }

  const mood = lesson.phase === 'recorded' ? 'happy' : lesson.explainerOpen ? 'reading' : 'think';

  return (
    <main className="mx-auto grid max-w-3xl gap-6 px-4 py-6 md:pl-24">
      <div className="flex items-center gap-4">
        <button type="button" onClick={lesson.exit} aria-label={COPY.lesson.exit} className="-ml-2 inline-flex size-11 shrink-0 items-center justify-center text-3xl leading-none text-muted hover:text-ink">
          <CloseMark className="size-7" />
        </button>
        <ProgressBar value={lesson.progress} label="Progresso da lição" />
        <span className="tabular text-lg text-muted">
          {lesson.position} de {lesson.total}
        </span>
      </div>
      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={lesson.question.id}
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -40 }}
          transition={{ type: 'spring', stiffness: 260, damping: 28 }}
          className="grid gap-6"
        >
          <div className="grid gap-3">
            <div className="flex items-center gap-3">
              <Mascot mood={mood} size={56} nodKey={lesson.nods} />
              <p className="text-base font-bold uppercase tracking-wider text-muted">{lesson.unit.label}</p>
            </div>
            <h1 className="text-[2rem] font-bold leading-tight md:text-5xl">{lesson.question.statement}</h1>
          </div>

          {lesson.phase === 'answer' ? (
            <>
              <ExplainerPanel
                context={lesson.question.context}
                sections={explainerSections(lesson.explainer)}
                open={lesson.explainerOpen}
                onToggle={lesson.setExplainerOpen}
              />
              <p className="text-xl text-muted">{lesson.question.options?.length ? COPY.lesson.askScale : COPY.lesson.ask}</p>
              <StanceOptions options={stanceOptionsFor(lesson.question, STANCES)} selected={lesson.stance} onSelect={lesson.chooseStance} />
              <ImportanceChips label={COPY.lesson.importance} options={IMPORTANCES} selected={lesson.importance} onSelect={lesson.chooseImportance} />
              <div className="flex flex-wrap gap-3">
                {lesson.canGoBack && (
                  <Button variant="quiet" onClick={lesson.back}>
                    <Chevron className="size-5 rotate-180" />
                    {COPY.lesson.back}
                  </Button>
                )}
                <Button variant="ghost" onClick={lesson.dontKnow}>
                  {COPY.lesson.dontKnow}
                </Button>
                <Button variant="primary" onClick={lesson.confirm} disabled={lesson.stance === null}>
                  {COPY.lesson.confirm}
                </Button>
              </div>
            </>
          ) : (
            <RecordedMoment skipped={lesson.saved === 'skip'} last={lesson.position >= lesson.total} onNext={lesson.next} />
          )}
        </motion.div>
      </AnimatePresence>
    </main>
  );
}

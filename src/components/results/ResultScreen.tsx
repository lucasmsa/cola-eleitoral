import { AnimatePresence, motion } from 'motion/react';
import { COPY } from '@/config/copy';
import { useResultFlow } from '@/hooks/useResultFlow';
import { AlignmentStep } from '../alignment/AlignmentStep';
import { Mascot } from '../shell/Mascot';
import { RestartQuiz } from '../shell/RestartQuiz';
import { Button, Hand } from '../shell/ui';
import { OfficeStep } from './OfficeStep';

export function ResultScreen() {
  const f = useResultFlow();
  return (
    <main className="mx-auto grid max-w-5xl grid-cols-[minmax(0,1fr)] gap-6 px-4 py-6 md:pl-24">
      <header className="flex flex-wrap items-center gap-4">
        <Mascot mood="cheer" size={88} />
        <div className="grid gap-1">
          <Hand className="text-2xl">{COPY.result.kicker(f.answered)}</Hand>
          <h1 className="text-5xl font-extrabold">{COPY.result.title}</h1>
        </div>
      </header>

      <nav aria-label={COPY.result.stepsLabel}>
        <ol className="grid grid-cols-2 gap-2 sm:flex sm:flex-wrap">
          {f.steps.map((s, i) => {
            const on = s.id === f.step;
            return (
              <li key={s.id}>
                <button
                  type="button"
                  onClick={() => f.go(s.id)}
                  aria-current={on ? 'step' : undefined}
                  className={`relative min-h-11 w-full rounded-md border-2 px-3 py-2 text-left text-base font-bold sm:w-auto md:text-lg ${on ? 'border-ink text-paper' : 'border-edge bg-paper text-ink hover:bg-fact'}`}
                >
                  {on && <motion.span layoutId="step-pill" className="absolute inset-0 rounded-[4px] bg-ink" transition={{ type: 'spring', stiffness: 400, damping: 32 }} />}
                  <span className="relative">
                    <span className="tabular">{i + 1}.</span> {s.label}
                  </span>
                </button>
              </li>
            );
          })}
        </ol>
      </nav>

      <AnimatePresence mode="wait" initial={false}>
        <motion.section
          key={f.step}
          initial={{ opacity: 0, x: 48 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -48 }}
          transition={{ type: 'spring', stiffness: 240, damping: 30 }}
          className="grid min-w-0 grid-cols-[minmax(0,1fr)] gap-6"
          aria-labelledby="step-title"
        >
          <h2 id="step-title" className="text-4xl font-extrabold">
            {f.current.label}
          </h2>
          {f.step === 'alinhamento' ? <AlignmentStep /> : <OfficeStep office={f.step} />}
        </motion.section>
      </AnimatePresence>

      <div className="flex flex-wrap items-center gap-3 border-t-2 border-rule pt-5">
        {f.prev && (
          <Button onClick={f.goPrev}>
            {COPY.result.prev}: {f.prev.label}
          </Button>
        )}
        <Button variant="pen" onClick={f.goNext}>
          {f.next ? `${COPY.result.next}: ${f.next.label}` : COPY.result.toCola}
        </Button>
      </div>
      <RestartQuiz />
    </main>
  );
}

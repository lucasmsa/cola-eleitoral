import { AnimatePresence, motion } from 'motion/react';
import { COPY } from '@/config/copy';
import { useReview } from '@/hooks/useReview';
import { optionState } from '@/lib/review';
import { CloseMark } from '../shell/icons';
import { Mascot } from '../shell/Mascot';
import { Portrait } from '../shell/Portrait';
import { Button, Hand, ProgressBar, SourceLink } from '../shell/ui';
import { QuizOption } from './QuizOption';

export function ReviewScreen() {
  const r = useReview();

  if (r.total === 0) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-8 md:pl-24">
        <h1 className="text-5xl font-extrabold">{COPY.review.title}</h1>
        <p className="mt-4 text-xl text-muted">{COPY.review.empty}</p>
      </main>
    );
  }

  if (r.phase === 'intro') {
    return (
      <main className="mx-auto grid max-w-3xl gap-6 px-4 py-8 md:pl-24">
        <motion.section
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid justify-items-start gap-5 rounded-md border-2 border-edge bg-paper p-6 shadow-[0_5px_0_#9aa6c2]"
        >
          <Mascot mood="think" size={96} />
          <h1 className="text-5xl font-extrabold leading-tight">{COPY.review.title}</h1>
          <p className="max-w-[60ch] text-xl">{COPY.review.intro}</p>
          <p className="max-w-[60ch] text-lg text-muted">{COPY.review.scope}</p>
          <Hand className="text-3xl">{COPY.review.count(r.total)}</Hand>
          <Button variant="pen" onClick={r.start}>
            {COPY.review.start}
          </Button>
        </motion.section>
      </main>
    );
  }

  if (r.phase === 'done') {
    return (
      <main className="mx-auto grid max-w-2xl justify-items-center gap-6 px-4 py-12 text-center">
        <Mascot mood="cheer" size={160} />
        <h1 className="text-5xl font-extrabold">{COPY.review.doneTitle}</h1>
        <p className="tabular text-3xl font-bold">{COPY.review.doneBody(r.hits, r.total)}</p>
        <div className="flex flex-wrap justify-center gap-3">
          {r.mistakes.length > 0 ? (
            <Button variant="primary" onClick={r.showMistakes}>
              {COPY.review.reviewMistakes(r.mistakes.length)}
            </Button>
          ) : (
            <p className="w-full text-lg text-muted">{COPY.review.noMistakes}</p>
          )}
          <Button variant="pen" onClick={r.goCola}>
            {COPY.review.toCola}
          </Button>
          <Button variant="quiet" onClick={r.again}>
            {COPY.review.again}
          </Button>
        </div>
      </main>
    );
  }

  if (r.phase === 'mistakes') {
    return (
      <main className="mx-auto grid max-w-3xl gap-6 px-4 py-8 md:pl-24">
        <h1 className="text-5xl font-extrabold">{COPY.review.mistakesTitle}</h1>
        <ol className="grid gap-5">
          {r.mistakes.map(({ card, picked }) => (
            <li key={card.id} className="grid gap-2 rounded-md border-2 border-edge bg-paper p-4">
              <p className="text-xl font-bold leading-snug">{card.prompt}</p>
              {card.quote && <blockquote className="border-l-4 border-pen pl-3 text-lg">“{card.quote}”</blockquote>}
              <p className="text-lg">
                <span className="text-muted">{COPY.review.yourPick}: </span>
                {card.options[picked]?.label}
              </p>
              <p className="text-lg">
                <span className="text-muted">{COPY.review.rightAnswer}: </span>
                <strong>{card.options[card.correct]?.label}</strong>
              </p>
              <p className="text-lg text-muted">{card.explanation}</p>
              <p className="text-base text-muted">
                Fonte: <SourceLink label={card.source.label} url={card.source.url} />
              </p>
            </li>
          ))}
        </ol>
        <div className="flex flex-wrap gap-3">
          <Button onClick={r.backToScore}>{COPY.review.backToScore}</Button>
          <Button variant="pen" onClick={r.goCola}>
            {COPY.review.toCola}
          </Button>
        </div>
      </main>
    );
  }

  const card = r.card;
  if (!card) return null;
  return (
    <main className="mx-auto grid max-w-3xl gap-6 px-4 py-6 md:pl-24">
      <div className="flex items-center gap-4">
        <button type="button" onClick={r.exit} aria-label={COPY.review.exit} className="-ml-2 inline-flex size-11 shrink-0 items-center justify-center text-muted hover:text-ink">
          <CloseMark className="size-7" />
        </button>
        <ProgressBar value={r.progress} label="Progresso do quiz" />
        <span className="tabular text-lg text-muted">
          {r.position} de {r.total}
        </span>
      </div>
      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={card.id}
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -40 }}
          transition={{ type: 'spring', stiffness: 260, damping: 28 }}
          className="grid gap-5"
        >
          <p className="text-base font-bold uppercase tracking-wider text-muted">{card.about}</p>
          <div className="grid gap-4 sm:grid-cols-[auto_minmax(0,1fr)] sm:items-start">
            {card.kind === 'vote' && <Portrait name={r.nameOf(card.candidateId)} file={r.portraitOf(card.candidateId)} size="card" taped />}
            <h1 className="min-w-0 text-[clamp(1.6rem,6.4vw,2.25rem)] font-bold leading-tight [overflow-wrap:anywhere]">{card.prompt}</h1>
          </div>
          {card.quote && (
            <blockquote className="rounded-md border-2 border-line border-l-8 border-l-pen bg-fact p-4 text-xl">“{card.quote}”</blockquote>
          )}
          <div className="grid gap-2" role="group" aria-label="Opções">
            {card.options.map((option, i) => (
              <QuizOption
                key={option.label}
                option={option}
                state={optionState(i, r.picked, card.correct)}
                disabled={r.picked !== null}
                portrait={r.picked !== null || card.kind === 'fact' ? r.portraitOf(option.candidateId) : null}
                onPick={() => r.pick(i)}
              />
            ))}
          </div>
          {r.picked !== null && (
            <motion.section
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid gap-3 rounded-md border-2 border-ink bg-fact p-4"
              aria-live="polite"
            >
              <Hand className="text-3xl">{r.correct ? COPY.review.correct : COPY.review.wrong}</Hand>
              <p className="text-lg leading-relaxed">{card.explanation}</p>
              <p className="text-base text-muted">
                Fonte: <SourceLink label={card.source.label} url={card.source.url} />
              </p>
              <div>
                <Button variant="pen" onClick={r.next}>
                  {r.position >= r.total ? COPY.review.finish : COPY.review.next}
                </Button>
              </div>
            </motion.section>
          )}
        </motion.div>
      </AnimatePresence>
    </main>
  );
}

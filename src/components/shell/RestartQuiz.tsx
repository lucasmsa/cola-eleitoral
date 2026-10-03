import { AnimatePresence, motion } from 'motion/react';
import { COPY } from '@/config/copy';
import { useRestart } from '@/hooks/useRestart';
import { Button } from './ui';

export function RestartQuiz() {
  const r = useRestart();
  return (
    <div className="grid justify-items-start gap-3">
      <AnimatePresence mode="wait" initial={false}>
        {r.asking ? (
          <motion.div
            key="ask"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="grid gap-3 rounded-md border-2 border-contra bg-contra-soft p-4"
            role="alertdialog"
            aria-labelledby="restart-q"
          >
            <p id="restart-q" className="text-lg font-semibold text-ink">
              {COPY.restart.question}
            </p>
            <div className="flex flex-wrap gap-3">
              <Button variant="primary" onClick={r.confirm}>
                {COPY.restart.confirm}
              </Button>
              <Button onClick={r.cancel}>{COPY.restart.cancel}</Button>
            </div>
          </motion.div>
        ) : (
          <motion.div key="btn" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <Button variant="quiet" onClick={r.ask}>
              {COPY.restart.button}
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

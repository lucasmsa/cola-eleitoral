import { AnimatePresence, motion } from 'motion/react';
import type { ReactNode } from 'react';
import { useDisclosure } from '@/hooks/useDisclosure';
import { Chevron } from './icons';

type Look = 'box' | 'dashed' | 'tab';

interface Props {
  summary: ReactNode;
  children: ReactNode;
  defaultOpen?: boolean;
  onToggle?: (open: boolean) => void;
  look?: Look;
  className?: string;
  testId?: string;
}

const FRAME: Record<Look, string> = {
  box: 'rounded-md border-2 border-edge bg-paper',
  dashed: 'rounded-md border-2 border-dashed border-edge',
  tab: '',
};

const EASE = [0.22, 1, 0.36, 1] as const;

export function Disclosure({ summary, children, defaultOpen = false, onToggle, look = 'box', className = '', testId }: Props) {
  const d = useDisclosure(defaultOpen, onToggle);
  const button = (
    <button
      type="button"
      aria-expanded={d.open}
      aria-controls={d.panelId}
      onClick={d.toggle}
      className={
        look === 'tab'
          ? `relative z-10 flex min-h-12 max-w-full items-center gap-3 border-2 border-edge bg-fact px-4 py-2.5 text-left text-xl font-bold shadow-[2px_-2px_0_#d7deec] ${d.open ? '-mb-[2px] rounded-t-lg border-b-0' : 'rounded-lg'}`
          : 'flex min-h-12 w-full items-center gap-3 p-3 text-left text-lg font-bold'
      }
    >
      <motion.span animate={{ rotate: d.open ? 90 : 0 }} transition={{ duration: 0.26, ease: EASE }} className="shrink-0">
        <Chevron className="size-5" />
      </motion.span>
      <span className="min-w-0 flex-1">{summary}</span>
    </button>
  );
  return (
    <div className={`${FRAME[look]} ${className}`} data-testid={testId}>
      {button}
      <AnimatePresence initial={false}>
        {d.open && (
          <motion.div
            id={d.panelId}
            key="panel"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.26, ease: EASE }}
            className="overflow-hidden"
          >
            <div className={look === 'tab' ? 'rounded-b-md rounded-tr-md border-2 border-edge bg-fact/70 p-4' : 'px-3 pb-3'}>{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

import { motion } from 'motion/react';
import { COPY } from '@/config/copy';
import { unitStatus } from '@/lib/lessons';
import { Button } from '../shell/ui';
import { TrailNode } from './TrailNode';

interface Props {
  index: number;
  label: string;
  blurb: string;
  answered: number;
  total: number;
  current: boolean;
  onOpen: () => void;
}

export function UnitStop({ index, label, blurb, answered, total, current, onOpen }: Props) {
  const action = COPY.home[unitStatus(answered, total)];
  return (
    <motion.li
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 260, damping: 26, delay: index * 0.06 }}
      className={`grid grid-cols-[auto_minmax(0,1fr)] items-center gap-x-4 gap-y-3 rounded-md border-2 bg-paper p-4 sm:grid-cols-[auto_minmax(0,1fr)_auto] ${current ? 'border-pen shadow-[0_4px_0_#c2410c]' : 'border-edge'}`}
    >
      <TrailNode index={index} progress={total ? answered / total : 0} done={answered === total && total > 0} />
      <div className="grid min-w-0 gap-1">
        <h3 className="text-2xl font-bold">{label}</h3>
        <p className="text-lg text-muted">{blurb}</p>
        <p className="tabular text-base text-muted">
          {answered} de {total} perguntas
        </p>
      </div>
      <Button
        variant={current ? 'pen' : 'ghost'}
        onClick={onOpen}
        aria-label={`${action}: ${label}`}
        className="col-span-2 w-full sm:col-span-1 sm:w-auto"
      >
        {action}
      </Button>
    </motion.li>
  );
}

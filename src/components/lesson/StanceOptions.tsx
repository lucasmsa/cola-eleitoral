import { motion } from 'motion/react';
import type { StanceOption } from '@/lib/positions';
import type { Stance } from '@/lib/score';
import { CheckMark } from '../shell/icons';

interface Props {
  options: StanceOption[];
  selected: Stance | null;
  onSelect: (value: Stance) => void;
}

export function StanceOptions({ options, selected, onSelect }: Props) {
  return (
    <div className="grid gap-2" role="radiogroup" aria-label="Sua posição">
      {options.map((o) => {
        const on = selected === o.value;
        return (
          <motion.button
            key={o.value}
            type="button"
            role="radio"
            aria-checked={on}
            onClick={() => onSelect(o.value)}
            whileTap={{ scale: 0.97 }}
            animate={on ? { scale: [1, 1.03, 1] } : { scale: 1 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
            className={`flex items-center justify-between rounded-md border-2 px-4 py-3 text-left text-xl font-semibold ${on ? 'border-pen bg-pen-soft text-ink shadow-[0_3px_0_#c2410c]' : 'border-edge bg-paper shadow-[0_3px_0_#9aa6c2] hover:bg-fact'}`}
          >
            <span>{o.label}</span>
            {on && (
              <motion.span
                initial={{ scale: 0, rotate: -30 }}
                animate={{ scale: 1, rotate: 0 }}
                className="text-pen"
                aria-hidden="true"
              >
                <CheckMark className="size-7" />
              </motion.span>
            )}
          </motion.button>
        );
      })}
    </div>
  );
}

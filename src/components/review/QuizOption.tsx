import { motion } from 'motion/react';
import type { OptionState, ReviewOption } from '@/lib/review';
import { CheckMark, CloseMark } from '../shell/icons';
import { Portrait } from '../shell/Portrait';

const STYLE: Record<OptionState, string> = {
  idle: 'border-edge bg-paper hover:bg-fact shadow-[0_3px_0_#9aa6c2]',
  right: 'border-favor bg-favor-soft',
  wrong: 'border-contra bg-contra-soft',
};

interface Props {
  option: ReviewOption;
  state: OptionState;
  disabled: boolean;
  portrait: string | null;
  onPick: () => void;
}

export function QuizOption({ option, state, disabled, portrait, onPick }: Props) {
  return (
    <motion.button
      type="button"
      disabled={disabled}
      onClick={onPick}
      whileTap={{ scale: disabled ? 1 : 0.97 }}
      className={`flex items-center gap-3 rounded-md border-2 px-4 py-3 text-left text-xl font-semibold disabled:cursor-default ${STYLE[state]}`}
    >
      {option.candidateId && <Portrait name={option.label} file={portrait} size="avatar" />}
      <span className="flex-1">{option.label}</span>
      {state === 'right' && <CheckMark className="size-7 text-favor" />}
      {state === 'wrong' && <CloseMark className="size-6 text-contra" />}
    </motion.button>
  );
}

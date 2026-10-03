import { motion } from 'motion/react';
import type { ButtonHTMLAttributes, ReactNode } from 'react';
import type { PositionTone } from '@/lib/positions';

type Variant = 'primary' | 'pen' | 'ghost' | 'quiet';

const VARIANTS: Record<Variant, string> = {
  primary: 'bg-ink text-paper border-ink shadow-[0_3px_0_#0b1222] hover:brightness-110 active:translate-y-[2px] active:shadow-none',
  pen: 'bg-pen text-white border-pen shadow-[0_3px_0_#7c2a08] hover:brightness-110 active:translate-y-[2px] active:shadow-none',
  ghost: 'bg-paper text-ink border-edge hover:bg-fact',
  quiet: 'bg-transparent text-ink border-transparent underline decoration-line underline-offset-4 hover:decoration-pen',
};

const SIZES = {
  md: 'min-h-12 px-5 py-2 text-lg',
  sm: 'min-h-11 px-3 py-1 text-base',
  link: 'min-h-11 px-0 py-1 text-base',
} as const;

export function Button({
  variant = 'ghost',
  size = 'md',
  className = '',
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; size?: keyof typeof SIZES }) {
  return (
    <button
      type="button"
      {...props}
      className={`inline-flex items-center justify-center gap-2 rounded-md border-2 font-bold transition disabled:opacity-50 ${SIZES[size]} ${VARIANTS[variant]} ${className}`}
    />
  );
}

const TONES: Record<PositionTone, string> = {
  favor: 'bg-favor-soft text-favor',
  contra: 'bg-contra-soft text-contra',
  meio: 'bg-fact text-muted',
};

export function ToneChip({ tone, children }: { tone: PositionTone; children: ReactNode }) {
  return <span className={`inline-flex items-center rounded-full px-3 py-0.5 text-base font-bold ${TONES[tone]}`}>{children}</span>;
}

export function Tag({ children, strong = false }: { children: ReactNode; strong?: boolean }) {
  return (
    <span
      className={`inline-flex items-center rounded-sm border px-2 py-0.5 text-sm font-semibold tracking-wide ${strong ? 'border-ink text-ink' : 'border-edge text-muted'}`}
    >
      {children}
    </span>
  );
}

export function ProgressBar({ value, label }: { value: number; label: string }) {
  return (
    <div
      className="h-4 flex-1 overflow-hidden rounded-full border-2 border-edge bg-paper"
      role="progressbar"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(value * 100)}
    >
      <motion.div className="h-full bg-pen" initial={false} animate={{ width: `${value * 100}%` }} transition={{ type: 'spring', stiffness: 140, damping: 22 }} />
    </div>
  );
}

export function SourceLink({ label, url }: { label: string; url: string }) {
  return (
    <a href={url} target="_blank" rel="noreferrer" className="[overflow-wrap:anywhere] text-base text-ink underline decoration-line underline-offset-4 hover:decoration-pen">
      {label}
    </a>
  );
}

export function Hand({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <span className={`font-hand text-pen ${className}`}>{children}</span>;
}

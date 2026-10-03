import type { Importance } from '@/lib/score';

interface Props {
  label: string;
  options: { value: Importance; label: string }[];
  selected: Importance;
  onSelect: (value: Importance) => void;
  compact?: boolean;
}

export function ImportanceChips({ label, options, selected, onSelect, compact = false }: Props) {
  return (
    <div className={`flex flex-wrap items-center gap-2 ${compact ? 'text-base' : 'text-lg'}`} role="radiogroup" aria-label={label}>
      <span className="mr-1 text-muted">{label}</span>
      {options.map((o) => {
        const on = o.value === selected;
        return (
          <button
            key={o.value}
            type="button"
            role="radio"
            aria-checked={on}
            onClick={() => onSelect(o.value)}
            className={`inline-flex min-h-11 items-center rounded-full border-2 px-4 font-semibold ${on ? 'border-ink bg-ink text-paper' : 'border-edge bg-paper text-ink hover:bg-fact'}`}
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}

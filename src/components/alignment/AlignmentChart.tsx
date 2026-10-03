import { motion } from 'motion/react';
import { AXIS_LABELS } from '@/config/alignment';
import { COPY } from '@/config/copy';
import { CHART, type Dot } from '@/lib/chart';

interface Props {
  dots: Dot[];
  focusedId: string | null;
  onFocus: (id: string | null) => void;
}

const S = CHART.size;
const P = CHART.pad;
/** Economic pole labels sit one line below the social one so the three bottom labels never collide. */
const LABEL_ROW = 40;
const MID = S / 2;
const GRID = Array.from({ length: 9 }, (_, i) => P + ((S - 2 * P) / 8) * i);

function Marker({ dot, active }: { dot: Dot; active: boolean }) {
  const r = active ? 9 : 7;
  switch (dot.kind) {
    case 'voce':
      return (
        <path
          d="M0,-14 L4,-4 L14,-4 L6,3 L9,13 L0,7 L-9,13 L-6,3 L-14,-4 L-4,-4 Z"
          className="fill-pen stroke-ink"
          strokeWidth={1.5}
        />
      );
    case 'politico':
      return <circle r={r} className="fill-ink stroke-paper" strokeWidth={2} />;
    case 'partido':
      return <rect x={-r} y={-r} width={r * 2} height={r * 2} rx={2} className="fill-paper stroke-ink" strokeWidth={2.5} />;
    default:
      return <rect x={-r} y={-r} width={r * 2} height={r * 2} transform="rotate(45)" className="fill-favor stroke-paper" strokeWidth={2} />;
  }
}

export function AlignmentChart({ dots, focusedId, onFocus }: Props) {
  const ordered = [...dots].sort((a, b) => Number(a.kind === 'voce') - Number(b.kind === 'voce'));
  return (
    <svg viewBox={`0 0 ${S} ${S + LABEL_ROW}`} className="w-full max-w-[640px] select-none" role="group" aria-label={COPY.alignment.chartLabel}>
      <rect x={P} y={P} width={S - 2 * P} height={S - 2 * P} className="fill-paper stroke-line" strokeWidth={1.5} />
      {GRID.map((g) => (
        <g key={g} className="stroke-rule" strokeWidth={1}>
          <line x1={g} y1={P} x2={g} y2={S - P} />
          <line x1={P} y1={g} x2={S - P} y2={g} />
        </g>
      ))}
      <defs>
        <marker id="axis-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" className="fill-ink" />
        </marker>
      </defs>
      <line x1={P - 8} y1={MID} x2={S - P + 8} y2={MID} className="stroke-ink" strokeWidth={2} markerStart="url(#axis-arrow)" markerEnd="url(#axis-arrow)" />
      <line x1={MID} y1={P - 8} x2={MID} y2={S - P + 8} className="stroke-ink" strokeWidth={2} markerStart="url(#axis-arrow)" markerEnd="url(#axis-arrow)" />
      <g className="fill-pen font-hand text-[21px] max-sm:text-[30px]">
        <text x={P} y={S - P + 34 + LABEL_ROW}>
          {AXIS_LABELS.economico.negative}
        </text>
        <text x={S - P} y={S - P + 34 + LABEL_ROW} textAnchor="end">
          {AXIS_LABELS.economico.positive}
        </text>
        <text x={MID} y={P - 16} textAnchor="middle">
          {AXIS_LABELS.social.positive}
        </text>
        <text x={MID} y={S - P + 34} textAnchor="middle">
          {AXIS_LABELS.social.negative}
        </text>
      </g>
      {ordered.map((dot, i) => {
        const active = focusedId === dot.id;
        return (
          <motion.g
            key={dot.id}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: 'spring', stiffness: 320, damping: 20, delay: Math.min(i * 0.025, 0.8) }}
            style={{ x: dot.cx, y: dot.cy }}
            tabIndex={0}
            role="button"
            aria-label={COPY.alignment.dotLabel(dot.label, dot.placement.x.n, dot.placement.y.n)}
            onMouseEnter={() => onFocus(dot.id)}
            onMouseLeave={() => onFocus(null)}
            onFocus={() => onFocus(dot.id)}
            onBlur={() => onFocus(null)}
            className="cursor-pointer outline-none"
          >
            <circle r={22} className="fill-transparent" />
            <Marker dot={dot} active={active} />
            {dot.labelDy !== 0 && (
              <line
                x1={0}
                y1={0}
                x2={dot.labelSide === 'right' ? 10 : -10}
                y2={dot.labelDy}
                className={`stroke-line ${active || dot.kind === 'voce' ? '' : 'max-sm:hidden'}`}
                strokeWidth={1.5}
              />
            )}
            <text
              x={dot.labelSide === 'right' ? (dot.kind === 'voce' ? 17 : 12) : dot.kind === 'voce' ? -17 : -12}
              y={5 + dot.labelDy}
              textAnchor={dot.labelSide === 'right' ? 'start' : 'end'}
              className={`${dot.kind === 'voce' ? 'fill-pen text-[20px] font-bold max-sm:text-[32px]' : 'fill-ink text-[15px] max-sm:text-[27px]'} ${active ? 'font-bold' : dot.kind === 'voce' ? '' : 'max-sm:hidden'}`}
              stroke="#fbfaf5"
              strokeWidth={4}
              style={{ paintOrder: 'stroke' }}
            >
              {dot.label}
            </text>
          </motion.g>
        );
      })}
    </svg>
  );
}

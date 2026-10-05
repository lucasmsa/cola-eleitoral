import { COPY } from '@/config/copy';
import type { ColaSlotView } from '@/hooks/useCola';
import { colaRowName } from '@/lib/colaView';

export function ColaCard({ views, title = COPY.cola.cardTitle, note }: { views: ColaSlotView[]; title?: string; note?: string | undefined }) {
  return (
    <div
      className="flex flex-col overflow-hidden rounded-[1.5mm] border border-[#111] bg-white px-[3mm] py-[2.5mm] text-[#111]"
      style={{ width: '85.6mm', height: '54mm', boxSizing: 'border-box' }}
      data-testid="cola-card"
    >
      <div className="flex items-baseline justify-between pb-[1mm]">
        <b className="font-hand text-[13pt] leading-none">{title}</b>
        <span className="text-[6.5pt]">{COPY.cola.cardPlace}</span>
      </div>
      {views.map((v) => (
        <div key={v.slot.id} className="grid flex-1 grid-cols-[3mm_1fr_auto] items-center gap-[1.5mm] border-t border-[#bbb] leading-none">
          <span className="text-[8pt] font-extrabold">{v.index + 1}</span>
          <span className="min-w-0 truncate text-[7pt]">
            <b>{v.slot.label}</b> {colaRowName(v.lookup)}
          </span>
          <span className="flex gap-[0.6mm]">
            {Array.from({ length: v.slot.digits }, (_, i) => (
              <i key={i} className="tabular grid h-[5.4mm] w-[4.3mm] place-items-center rounded-[0.6mm] border-[1.2px] border-[#111] text-[10pt] font-bold not-italic">
                {v.lookup.status === 'branco' ? '' : (v.digits[i] ?? '')}
              </i>
            ))}
          </span>
        </div>
      ))}
      {note && <p className="border-t border-[#bbb] pt-[1mm] text-[6.5pt] leading-tight">{note}</p>}
    </div>
  );
}

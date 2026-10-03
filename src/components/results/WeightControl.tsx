import { COPY } from '@/config/copy';
import type { Weights } from '@/lib/score';
import { percent } from '@/lib/text';
import { Disclosure } from '../shell/Disclosure';

export function WeightControl({
  weights,
  onChange,
}: {
  weights: Weights;
  onChange: (record: number) => void;
}) {
  return (
    <Disclosure
      summary={
        <>
          {COPY.results.weightsTitle}: {COPY.results.record} {percent(weights.record)},{' '}
          {COPY.results.platform} {percent(weights.platform)}
        </>
      }
    >
      <div className="grid gap-3">
        <p className="max-w-[70ch] text-lg text-muted">{COPY.results.weightsExplain}</p>
        <label htmlFor="record-weight" className="text-lg font-semibold">
          {COPY.results.record} {percent(weights.record)}
        </label>
        <input
          id="record-weight"
          type="range"
          min={0}
          max={1}
          step={0.1}
          value={weights.record}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full max-w-md accent-pen"
        />
      </div>
    </Disclosure>
  );
}

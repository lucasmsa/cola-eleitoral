import { motion } from 'motion/react';
import { KIND_LABELS } from '@/config/alignment';
import { COPY } from '@/config/copy';
import type { EntityKind, RankedEntity } from '@/lib/alignment';
import { percent } from '@/lib/text';

export function AlignedLists({ ranked }: { ranked: Record<EntityKind, RankedEntity[]> }) {
  return (
    <section className="grid gap-4" aria-labelledby="aligned-title">
      <h2 id="aligned-title" className="text-3xl font-bold">
        {COPY.alignment.listsTitle}
      </h2>
      <p className="max-w-[70ch] text-lg text-muted">{COPY.alignment.listsExplain}</p>
      <div className="grid gap-6 lg:grid-cols-3">
        {(Object.keys(KIND_LABELS) as EntityKind[]).map((kind) => (
          <div key={kind} className="grid content-start gap-3">
            <h3 className="text-2xl font-bold">{KIND_LABELS[kind]}</h3>
            {ranked[kind].length === 0 && <p className="text-lg text-muted">{COPY.alignment.noneYet}</p>}
            <ol className="grid gap-3">
              {ranked[kind].map((r, i) => (
                <motion.li
                  key={r.entity.id}
                  initial={{ opacity: 0, x: -16 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="grid gap-1"
                >
                  <div className="flex items-baseline justify-between gap-3">
                    <span className="text-lg font-semibold">
                      <span className="tabular mr-2 text-pen">{i + 1}</span>
                      {r.entity.label}
                    </span>
                    <span className="tabular text-xl font-extrabold">{percent(r.agreement.score ?? 0)}</span>
                  </div>
                  <div className="h-3 overflow-hidden rounded-full border border-edge bg-paper" aria-hidden="true">
                    <motion.div
                      className="h-full bg-pen"
                      initial={{ width: 0 }}
                      animate={{ width: `${(r.agreement.score ?? 0) * 100}%` }}
                      transition={{ type: 'spring', stiffness: 120, damping: 20, delay: i * 0.05 }}
                    />
                  </div>
                  <span className="text-base text-muted">
                    {r.entity.detail}, {COPY.alignment.common(r.agreement.common)}
                  </span>
                </motion.li>
              ))}
            </ol>
          </div>
        ))}
      </div>
    </section>
  );
}

import type { ReactNode } from 'react';
import { COPY } from '@/config/copy';
import { useDataInfo } from '@/hooks/useDataInfo';
import { InfoMark } from './icons';

export function DataInfo({ children }: { children: ReactNode }) {
  const { rootRef, buttonRef, open, panelId, freshness: f, toggle } = useDataInfo();
  const t = COPY.dataInfo;
  return (
    <div ref={rootRef} className="grid gap-2">
      <div className="flex items-start gap-1">
        <div className="min-w-0 flex-1">{children}</div>
        <button
          ref={buttonRef}
          type="button"
          aria-label={t.button}
          aria-expanded={open}
          aria-controls={panelId}
          onClick={toggle}
          className="-my-2 inline-flex size-11 shrink-0 items-center justify-center rounded-full text-muted hover:text-ink"
        >
          <InfoMark className="size-5" />
        </button>
      </div>
      {open && (
        <div id={panelId} role="region" aria-label={t.button} className="grid gap-3 rounded-md border-2 border-edge bg-paper p-4 text-base shadow-[3px_3px_0_#d7deec]">
          <p className="text-lg font-bold">{t.title}</p>
          <dl className="grid gap-2 sm:grid-cols-[auto_1fr] sm:gap-x-4">
            <dt className="font-semibold">{t.candidatos}</dt>
            <dd className="tabular text-muted">{f.candidatos ?? t.unknown}</dd>
            <dt className="font-semibold">{t.resultados}</dt>
            <dd className="tabular text-muted">{f.resultados ?? t.unknown}</dd>
            <dt className="font-semibold">{t.evidencias}</dt>
            <dd className="tabular text-muted">{f.evidencias}</dd>
            <dt className="font-semibold">{t.pesquisas}</dt>
            <dd className="text-muted">
              <ul className="grid gap-1">
                {f.pesquisas.map((p) => (
                  <li key={`${p.office}-${p.institute}-${p.field}`}>
                    <span className="font-semibold text-ink">{p.office}</span>, {p.institute}: <span className="tabular">{p.field}</span>
                  </li>
                ))}
              </ul>
            </dd>
          </dl>
          <p className="text-muted">{t.caveat}</p>
        </div>
      )}
    </div>
  );
}

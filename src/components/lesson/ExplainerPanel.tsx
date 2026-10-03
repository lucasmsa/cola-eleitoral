import { COPY } from '@/config/copy';
import type { ExplainerSection } from '@/lib/explainers';
import { Disclosure } from '../shell/Disclosure';
import { SourceLink } from '../shell/ui';

interface Props {
  context: string;
  sections: ExplainerSection[];
  open: boolean;
  onToggle: (open: boolean) => void;
}

export function ExplainerPanel({ context, sections, open, onToggle }: Props) {
  if (sections.length === 0 && !context) return null;
  return (
    <Disclosure look="tab" defaultOpen={open} onToggle={onToggle} summary={COPY.explainer.title}>
      <div className="grid gap-5">
        {sections.length === 0 && <p className="text-lg">{context}</p>}
        {sections.map((s) => (
          <section key={s.key} className="grid gap-2">
            <h3 className="font-hand text-2xl font-bold text-pen">{s.title}</h3>
            <ul className="grid gap-3">
              {s.claims.map((c) => (
                <li key={c.checkId} className="grid gap-1 border-l-2 border-line pl-3">
                  <p className="text-lg leading-relaxed">{c.text}</p>
                  <p className="text-base text-muted">
                    {COPY.fact.source}: <SourceLink label={c.source.label} url={c.source.url} />
                  </p>
                </li>
              ))}
            </ul>
          </section>
        ))}
        {sections.length === 0 && <p className="text-base text-muted">{COPY.explainer.pending}</p>}
      </div>
    </Disclosure>
  );
}

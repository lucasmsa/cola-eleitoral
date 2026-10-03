import { useMemo, useState } from 'react';
import { AXIS_LABELS, directionLabel } from '@/config/alignment';
import { axes, candidates, countries, evidence, portraits, profiles, questions } from '@/data';
import { indexPortraits } from '@/lib/portraits';
import type { Axis } from '@/data/schema';
import { answerPositions, placeOnAxes, rankAligned, MIN_PER_AXIS, type EntityKind } from '@/lib/alignment';
import { plotDots, type Dot } from '@/lib/chart';
import { buildCountries, buildParties, buildPoliticians, chartPoliticians } from '@/lib/entities';
import { buildCatalog } from '@/lib/subjects';
import { useAnswersStore } from '@/stores/answers';

const catalog = buildCatalog(candidates);
const statements = new Map(questions.map((q) => [q.id, q.statement]));
const RANK_LIMIT = 8;
const portraitIndex = indexPortraits(portraits);

export interface MethodRow {
  questionId: string;
  statement: string;
  direction: string;
  rationale: string;
}

export function useAlignment() {
  const answers = useAnswersStore((s) => s.answers);
  const weights = useAnswersStore((s) => s.weights);
  const [shown, setShown] = useState<Record<EntityKind, boolean>>({ politico: true, partido: true, pais: true });
  const [focused, setFocused] = useState<string | null>(null);

  const groups = useMemo(
    () => ({
      politico: buildPoliticians(candidates, evidence, weights),
      partido: buildParties(evidence, catalog, weights),
      pais: buildCountries(countries),
    }),
    [weights],
  );

  const you = useMemo(() => placeOnAxes(answerPositions(answers), axes), [answers]);

  const plot = useMemo(() => {
    const items = [
      { id: 'voce', label: 'Você', detail: 'Suas respostas', kind: 'voce' as const, positions: answerPositions(answers) },
      ...(shown.politico ? chartPoliticians(groups.politico, profiles).map((p) => ({ ...p, portrait: portraitIndex.get(p.id)?.file ?? null })) : []),
      ...(shown.partido ? groups.partido : []),
      ...(shown.pais ? groups.pais : []),
    ];
    return plotDots(items, axes);
  }, [answers, groups, shown]);

  const ranked = useMemo(
    () => ({
      politico: rankAligned(groups.politico, answers).slice(0, RANK_LIMIT),
      partido: rankAligned(groups.partido, answers).slice(0, RANK_LIMIT),
      pais: rankAligned(groups.pais, answers).slice(0, RANK_LIMIT),
    }),
    [groups, answers],
  );

  const method = useMemo(() => {
    const byAxis: Record<Axis, MethodRow[]> = { economico: [], social: [] };
    for (const a of axes) {
      byAxis[a.axis].push({
        questionId: a.questionId,
        statement: statements.get(a.questionId) ?? a.questionId,
        direction: directionLabel(a.axis, a.direction),
        rationale: a.rationale,
      });
    }
    return (['economico', 'social'] as Axis[]).map((axis) => ({ axis, label: AXIS_LABELS[axis].name, rows: byAxis[axis] }));
  }, []);

  const focusedDot: Dot | null = plot.dots.find((d) => d.id === focused) ?? null;

  return {
    hasAxes: axes.length > 0,
    you,
    minPerAxis: MIN_PER_AXIS,
    dots: plot.dots,
    hiddenByKind: (['politico', 'partido', 'pais'] as EntityKind[])
      .map((kind) => ({ kind, n: plot.hidden.filter((h) => h.kind === kind).length }))
      .filter((h) => h.n > 0),
    youVisible: you.visible,
    shown,
    toggle: (kind: EntityKind) => setShown((s) => ({ ...s, [kind]: !s[kind] })),
    focusedDot,
    focus: setFocused,
    ranked,
    method,
  };
}

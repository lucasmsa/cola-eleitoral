import { useMemo, useState } from 'react';
import { OFFICE_BY_ID, type ColaSlotId } from '@/config/election';
import { candidates, controversies, evidence, polls, portraits, profiles, questions } from '@/data';
import { controversiesOf } from '@/lib/controversies';
import { indexPortraits } from '@/lib/portraits';
import type { Candidate, Office } from '@/data/schema';
import { listParties } from '@/lib/cola';
import { rankCandidates, rankLists } from '@/lib/results';
import { defendsEvidence, profilesFor } from '@/lib/profiles';
import { buildRows, type ResultRow } from '@/lib/rows';
import { buildCatalog } from '@/lib/subjects';
import { useAnswersStore } from '@/stores/answers';
import { useScreenStore } from '@/stores/screen';

const catalog = buildCatalog(candidates);
const statements = new Map(questions.map((q) => [q.id, q.statement]));
const portraitIndex = indexPortraits(portraits);

const SLOTS_BY_OFFICE: Record<Office, ColaSlotId[]> = {
  presidente: ['presidente'],
  governador: ['governador'],
  senador: ['senador_1', 'senador_2'],
  deputado_federal: ['deputado_federal'],
  deputado_estadual: ['deputado_estadual'],
};

export type { ResultRow };

export function useResults(office: Office) {
  const go = useScreenStore((s) => s.go);
  const config = OFFICE_BY_ID[office];
  const answers = useAnswersStore((s) => s.answers);
  const weights = useAnswersStore((s) => s.weights);
  const cola = useAnswersStore((s) => s.cola);
  const setCola = useAnswersStore((s) => s.setCola);
  const setRecordWeight = useAnswersStore((s) => s.setRecordWeight);
  const [listId, setListId] = useState<string | null>(null);
  const [detail, setDetail] = useState<{ type: 'candidate' | 'list'; id: string } | null>(null);
  const [legendaFor, setLegendaFor] = useState<string | null>(null);

  const listFirst = config.listFirst;
  const lists = useMemo(
    () =>
      listFirst
        ? buildRows(rankLists(office, candidates, evidence, answers, weights), 'list', catalog, answers, evidence)
        : null,
    [listFirst, office, answers, weights],
  );
  const people = useMemo(() => {
    if (listFirst && listId === null) return null;
    const ranking = rankCandidates(office, candidates, questions, evidence, answers, weights, listId ?? undefined);
    return buildRows(ranking, 'candidate', catalog, answers, evidence, (id) => portraitIndex.get(id)?.file ?? null);
  }, [listFirst, office, answers, weights, listId]);

  const slots = SLOTS_BY_OFFICE[office];

  function colaSlotOf(row: ResultRow): ColaSlotId | null {
    if (row.type === 'candidate' && row.number) {
      return slots.find((s) => {
        const e = cola[s];
        return e?.kind === 'number' && e.digits === row.number;
      }) ?? null;
    }
    return null;
  }

  function putInCola(row: ResultRow) {
    if (row.type === 'list') {
      setLegendaFor(row.id);
      return;
    }
    if (!row.number) return;
    const free = slots.find((s) => !cola[s]);
    if (!free) return;
    setCola(free, { kind: 'number', digits: row.number });
  }

  function removeFromCola(slot: ColaSlotId) {
    setCola(slot, null);
  }

  function pickLegenda(number: string) {
    const slot = slots[0];
    if (slot) setCola(slot, { kind: 'number', digits: number });
    setLegendaFor(null);
  }

  const legendaParties = legendaFor ? listParties(legendaFor, office, candidates) : [];

  return {
    office,
    config,
    weights,
    setRecordWeight,
    answeredTotal: Object.values(answers).filter((a) => a !== 'skip').length,
    lists,
    listId,
    listName: listId ? (catalog.listNames.get(listId) ?? listId) : null,
    selectList: (id: string | null) => setListId(id),
    people,
    profiles: (listFirst && listId === null ? [] : profilesFor(profiles, office, catalog.candidates, listId ?? undefined)).map((p) => ({
      profile: p,
      candidate: catalog.candidates.get(p.candidateId) ?? null,
      defends: defendsEvidence(p, evidence),
      controversies: controversiesOf(controversies, p.candidateId),
      portrait: portraitIndex.get(p.candidateId)?.file ?? null,
    })),
    portraitOf: (id: string) => portraitIndex.get(id)?.file ?? null,
    statementOf: (questionId: string) => statements.get(questionId) ?? '',
    listNameOf: (c: Candidate | null) => (c ? (catalog.listNames.get(c.list) ?? c.listName) : ''),
    polls: polls.filter((p) => p.office === office),
    detail,
    openDetail: (row: ResultRow) => setDetail({ type: row.type, id: row.id }),
    closeDetail: () => setDetail(null),
    colaSlotOf,
    slotsFull: slots.every((s) => cola[s]),
    putInCola,
    removeFromCola,
    legendaFor: legendaFor ? (catalog.listNames.get(legendaFor) ?? legendaFor) : null,
    legendaParties,
    pickLegenda,
    cancelLegenda: () => setLegendaFor(null),
    colaLegenda: (() => {
      const e = slots[0] ? cola[slots[0]] : undefined;
      return config.listFirst && e?.kind === 'number' && e.digits.length === 2 ? e.digits : null;
    })(),
    goCola: () => go({ name: 'cola' }),
    goHome: () => go({ name: 'home' }),
  };
}

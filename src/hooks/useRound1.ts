import { useMemo } from 'react';
import { COPY } from '@/config/copy';
import { portraits, round1 } from '@/data';
import type { ResultSource, Turnout } from '@/data/schema';
import { indexPortraits } from '@/lib/portraits';
import { barRows, electedByList, formatInt, pickOutcomes, type BarRow, type ListGroup, type PickRow } from '@/lib/round1';
import { useAnswersStore } from '@/stores/answers';
import { useNav } from './useNav';

export interface TurnoutView {
  scope: string;
  lines: string[];
  note: string | null;
  source: ResultSource;
}

function turnoutView(scope: string, t: Turnout, source: ResultSource): TurnoutView {
  return {
    scope,
    lines: [
      COPY.round1.turnoutLine(t.comparecimentoPct, formatInt(t.comparecimento)),
      COPY.round1.abstencao(t.abstencaoPct, formatInt(t.abstencao)),
      COPY.round1.brancos(t.brancosPct, formatInt(t.brancos)),
      COPY.round1.nulos(t.nulosPct, formatInt(t.nulos)),
    ],
    note: t.eleitoresSecoesNaoInstaladas > 0 ? COPY.round1.secoes(formatInt(t.eleitoresSecoesNaoInstaladas)) : null,
    source,
  };
}

export function useRound1() {
  const cola = useAnswersStore((s) => s.cola);
  const nav = useNav();
  const portraitIndex = useMemo(() => indexPortraits(portraits), []);
  const runoff = round1.presidente.br.candidates.filter((c) => c.status === '2º turno').map((c) => c.candidateId);
  const presidenteBr: BarRow[] = useMemo(() => barRows(round1.presidente.br, runoff), [runoff]);
  const presidentePb: BarRow[] = useMemo(() => barRows(round1.presidente.pb, runoff), [runoff]);
  const governador = useMemo(() => barRows(round1.governador), []);
  const senador = useMemo(() => barRows(round1.senador), []);
  const depFederal: ListGroup[] = useMemo(() => electedByList(round1.deputadoFederal), []);
  const depEstadual: ListGroup[] = useMemo(() => electedByList(round1.deputadoEstadual), []);
  const picks: PickRow[] = useMemo(() => pickOutcomes(cola, round1), [cola]);
  const br = round1.presidente.br;
  const pb = round1.presidente.pb;
  return {
    presidenteBr,
    presidentePb,
    presidenteSources: { br: br.source, pb: pb.source },
    governador,
    governadorSource: round1.governador.source,
    senador,
    senadorSource: round1.senador.source,
    depFederal,
    depFederalTotal: round1.deputadoFederal.seatsTotal,
    depFederalSource: round1.deputadoFederal.source,
    depEstadual,
    depEstadualTotal: round1.deputadoEstadual.seatsTotal,
    depEstadualSource: round1.deputadoEstadual.source,
    turnout: [
      br.turnout ? turnoutView(COPY.round1.brasil, br.turnout, br.source) : null,
      pb.turnout ? turnoutView(COPY.round1.paraiba, pb.turnout, pb.source) : null,
    ].filter((t): t is TurnoutView => t !== null),
    picks,
    openRound1: nav.goRound1,
    summary: {
      runoff: presidenteBr.filter((c) => c.status === '2º turno'),
      governor: governador.find((c) => c.elected) ?? null,
      senators: senador.filter((c) => c.elected),
    },
    portraitOf: (candidateId: string) => portraitIndex.get(candidateId)?.file ?? null,
  };
}

import { useMemo } from 'react';
import { COLA2_SLOTS, type ColaSlot } from '@/config/election';
import { COPY } from '@/config/copy';
import { candidates, endorsements, evidence, polls2, portraits, questions, round2 } from '@/data';
import { lookupSlot, sanitizeDigits } from '@/lib/cola';
import { longDate } from '@/lib/days';
import { buildUnits } from '@/lib/lessons';
import { indexPortraits } from '@/lib/portraits';
import { answerLabel, positionTone, POSITION_LABEL, type PositionTone } from '@/lib/positions';
import { measuredLabel } from '@/lib/results';
import { finalistCoverage, firstMissingUnit, headToHead, missingQuestions, round2Candidates, winnerOf } from '@/lib/round2';
import type { SubjectScore } from '@/lib/score';
import { brDate, titleCase } from '@/lib/text';
import { useAnswersStore } from '@/stores/answers';
import type { Evidence, Poll, Question } from '@/data/schema';
import type { ColaSlotView } from './useCola';
import { useNav } from './useNav';

export interface FinalistView {
  id: string;
  name: string;
  number: string;
  pctBrasil: string;
  pctParaiba: string;
  portrait: string | null;
  score: SubjectScore;
  coverage: string;
  measured: string;
}

export interface SideView {
  finalistId: string;
  name: string;
  tone: PositionTone | null;
  label: string;
  evidence: Evidence[];
}

export interface RowView {
  question: Question;
  you: string;
  answered: boolean;
  sides: SideView[];
}

const OFFICE = 'presidente';

export function useRound2() {
  const answers = useAnswersStore((s) => s.answers);
  const weights = useAnswersStore((s) => s.weights);
  const cola2 = useAnswersStore((s) => s.cola2);
  const setCola2 = useAnswersStore((s) => s.setCola2);
  const nav = useNav();
  const units = useMemo(() => buildUnits(questions), []);
  const portraitIndex = useMemo(() => indexPortraits(portraits), []);
  const h = useMemo(() => headToHead(round2, OFFICE, questions, evidence, answers, weights), [answers, weights]);
  const missing = missingQuestions(h, answers);
  const missingUnit = firstMissingUnit(units, missing);

  const finalists: FinalistView[] = h.finalists.map((f) => {
    const cov = finalistCoverage(h, answers, f.candidateId);
    const score = h.scores[f.candidateId]!;
    return {
      id: f.candidateId,
      name: titleCase(f.ballotName),
      number: f.number,
      pctBrasil: f.pctBrasil,
      pctParaiba: f.pctParaiba,
      portrait: portraitIndex.get(f.candidateId)?.file ?? null,
      score,
      coverage: COPY.results.coverage(cov.covered, cov.answered),
      measured: measuredLabel(score.measuredShare),
    };
  });
  const names = Object.fromEntries(finalists.map((f) => [f.id, f.name]));

  const rows: RowView[] = h.rows.map((r) => {
    const answer = answers[r.question.id];
    const you =
      answer === undefined ? COPY.round2.youMissing : answer === 'skip' ? COPY.round2.youSkipped : answerLabel(r.question, answer.stance);
    return {
      question: r.question,
      you,
      answered: answer !== undefined && answer !== 'skip',
      sides: h.finalists.map((f) => {
        const side = r.sides[f.candidateId]!;
        const tone = side.position === null ? null : positionTone(side.position);
        return {
          finalistId: f.candidateId,
          name: names[f.candidateId] ?? f.ballotName,
          tone,
          label: tone ? POSITION_LABEL[tone] : COPY.round2.noPosition,
          evidence: side.evidence,
        };
      }),
    };
  });

  const governor = winnerOf(round2, 'governador');
  const dateLabel = longDate(round2.date);
  const numbers = h.finalists.map((f) => f.number).sort().join(' e ');
  const allowed = round2Candidates(round2, candidates);
  const colaViews: ColaSlotView[] = COLA2_SLOTS.map((slot, index) => {
    const entry = cola2[slot.id];
    return {
      slot,
      index,
      entry,
      digits: entry?.kind === 'number' ? entry.digits : '',
      lookup: lookupSlot(slot, entry, allowed),
    };
  });
  const sources = round2.offices.flatMap((o) => o.sources);

  const pollCaption = (p: Poll) =>
    COPY.round2.pollCaption(brDate(p.fieldStart), brDate(p.fieldEnd), COPY.round2.pollBasis(p.institute));
  return {
    endorsements,
    polls2,
    pollCaption,
    finalists,
    rows,
    missingCount: missing.length,
    canNudge: missing.length > 0 && missingUnit !== null,
    governor: governor ? { name: titleCase(governor.ballotName), pct: governor.pct } : null,
    dateLabel,
    numbers,
    sources,
    colaViews,
    colaTitle: COPY.round2.cardTitle(dateLabel),
    colaNote: governor ? COPY.round2.cardNote(titleCase(governor.ballotName)) : undefined,
    notFoundText: COPY.round2.notFinalist(numbers),
    typeDigits: (slot: ColaSlot, raw: string) => {
      const digits = sanitizeDigits(raw, slot.digits);
      setCola2(slot.id, digits ? { kind: 'number', digits } : null);
    },
    setBranco: (slot: ColaSlot) => setCola2(slot.id, { kind: 'branco' }),
    clear: (slot: ColaSlot) => setCola2(slot.id, null),
    print: () => window.print(),
    answerMissing: () => missingUnit && nav.goLesson(missingUnit),
    openRound2: nav.goRound2,
    openProfiles: () => nav.goResultStep('presidente'),
    openAlignment: () => nav.goResultStep('alinhamento'),
  };
}

import { useMemo } from 'react';
import { IMPORTANCES } from '@/config/answers';
import { OFFICE_BY_ID } from '@/config/election';
import { candidates, evidence, questions } from '@/data';
import type { Evidence, Office } from '@/data/schema';
import { answerLabel, POSITION_LABEL, positionTone, type PositionTone } from '@/lib/positions';
import { questionsForOffice } from '@/lib/results';
import { blendPosition, type Importance } from '@/lib/score';
import { buildCatalog, describeSubject, evidenceBadge, type EvidenceBadge } from '@/lib/subjects';
import { useAnswersStore } from '@/stores/answers';

const catalog = buildCatalog(candidates);

export interface DetailRow {
  questionId: string;
  statement: string;
  yourAnswer: string;
  importance: Importance | null;
  theirTone: PositionTone | null;
  theirLabel: string;
  measured: boolean;
  evidence: { item: Evidence; badge: EvidenceBadge }[];
}

export function useSubjectDetail(subject: { type: 'candidate' | 'list'; id: string }, office: Office) {
  const answers = useAnswersStore((s) => s.answers);
  const weights = useAnswersStore((s) => s.weights);
  const setImportance = useAnswersStore((s) => s.setImportance);
  const info = describeSubject(catalog, subject);

  const rows = useMemo<DetailRow[]>(() => {
    const scope = subject.type === 'list' ? questions : questionsForOffice(questions, office);
    const own = evidence.filter((e) => e.subject.type === subject.type && e.subject.id === subject.id);
    const mapped = scope.map((q) => {
      const items = own.filter((e) => e.questionId === q.id);
      const blended = blendPosition(items, weights);
      const answer = answers[q.id];
      const tone = blended ? positionTone(blended.position) : null;
      return {
        questionId: q.id,
        statement: q.statement,
        yourAnswer: answer === undefined ? 'Sem resposta' : answer === 'skip' ? 'Pulou' : answerLabel(q, answer.stance),
        importance: answer && answer !== 'skip' ? answer.importance : null,
        theirTone: tone,
        theirLabel: tone ? POSITION_LABEL[tone] : 'Sem evidência checada',
        measured: blended?.measured ?? false,
        evidence: items.map((item) => ({ item, badge: evidenceBadge(item) })),
      };
    });
    return [...mapped.filter((r) => r.evidence.length > 0), ...mapped.filter((r) => r.evidence.length === 0)];
  }, [subject.type, subject.id, office, answers, weights]);

  const c = info.candidate;
  return {
    info,
    officeLabel: c ? OFFICE_BY_ID[c.office].label : 'Partido ou federação',
    runningMates: c?.runningMates ?? [],
    elected: c?.elected ?? [],
    status: c?.status ?? null,
    planUrl: c?.planUrl ?? null,
    rows,
    importances: IMPORTANCES,
    setImportance,
  };
}

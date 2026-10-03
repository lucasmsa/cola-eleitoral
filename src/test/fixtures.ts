import type { Candidate, Evidence, Question } from '@/data/schema';

const src = { url: 'https://example.org', accessed: '2026-09-30', label: 'Fonte' };

export function cand(id: string, partial: Partial<Candidate> = {}): Candidate {
  const [office, number] = id.split('-') as [Candidate['office'], string];
  return {
    id,
    office,
    number,
    ballotName: `NOME ${number}`,
    party: 'PX',
    list: 'PX',
    listName: 'PX',
    runningMates: [],
    status: 'DEFERIDO',
    withdrawn: false,
    elected: [],
    source: src,
    ...partial,
  };
}

export function ev(subjectId: string, questionId: string, partial: Partial<Evidence> = {}): Evidence {
  return {
    id: `${subjectId}:${questionId}:${partial.detail ?? ''}`,
    subject: { type: 'candidate', id: subjectId },
    questionId,
    kind: 'record',
    position: 1,
    detail: 'Votou SIM na PEC 1/2023 (teste), 1º turno na Câmara, 01/01/2023.',
    date: '2023-01-01',
    source: src,
    checkId: 'c',
    lowDiscrimination: false,
    ...partial,
  };
}

export function q(id: string, partial: Partial<Question> = {}): Question {
  return {
    id,
    area: 'economia',
    offices: ['presidente', 'senador', 'deputado_federal'],
    statement: `Afirmação ${id}`,
    context: '',
    sources: [],
    ...partial,
  };
}

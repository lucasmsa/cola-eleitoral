import { OFFICE_BY_ID } from '@/config/election';
import type { Claim, Evidence, Office, Profile, Question, Source } from '@/data/schema';
import { seededRandom, shuffle } from './random';
import { describeSubject, type Catalog } from './subjects';

export type ReviewKind = 'vote' | 'quote' | 'fact';

export interface ReviewOption {
  label: string;
  candidateId: string | null;
}

export interface ReviewCard {
  id: string;
  kind: ReviewKind;
  candidateId: string | null;
  about: string;
  prompt: string;
  quote: string | null;
  options: ReviewOption[];
  correct: number;
  explanation: string;
  source: Source;
}

export const VOTE_OPTIONS: ReviewOption[] = [
  { label: 'A favor (votou SIM)', candidateId: null },
  { label: 'Contra (votou NÃO)', candidateId: null },
];

const QUIZ_OFFICES = new Set<Office>(['presidente', 'governador', 'senador']);

/** Only the candidates the user meets on the result screen: profiled, majoritarian, still in the race. */
export function quizCandidates(profiles: Profile[], catalog: Catalog): Set<string> {
  return new Set(
    profiles
      .filter((p) => QUIZ_OFFICES.has(p.office))
      .map((p) => p.candidateId)
      .filter((id) => {
        const c = catalog.candidates.get(id);
        return c !== undefined && !c.withdrawn;
      }),
  );
}

export interface ParsedVote {
  vote: 'SIM' | 'NÃO';
  code: string;
  topic: string | null;
  where: string;
}

const VOTE_DETAIL = /^Votou (SIM|NÃO) (?:na|no|nas|nos|em) (.+?)\.?$/;

/** "Votou SIM na MP 1.031/2021 (privatização da Eletrobras) na Câmara, 19/05/2021 (então no DEM)." */
export function parseVote(detail: string): ParsedVote | null {
  const m = VOTE_DETAIL.exec(detail);
  if (!m) return null;
  const vote = m[1] as 'SIM' | 'NÃO';
  const measure = (m[2] as string).replace(/\s*\(então [^)]*\)\s*$/, '');
  const open = measure.indexOf(' (');
  const close = open >= 0 ? measure.indexOf(')', open) : -1;
  if (open < 0 || close < 0) return { vote, code: measure, topic: null, where: '' };
  return {
    vote,
    code: measure.slice(0, open),
    topic: measure.slice(open + 2, close),
    where: measure.slice(close + 1).replace(/^[,\s]+/, ''),
  };
}

function lowerFirst(text: string): string {
  return text.charAt(0).toLocaleLowerCase('pt-BR') + text.slice(1);
}

function voteCards(evidence: Evidence[], catalog: Catalog, allowed: Set<string>, statements: Map<string, string>): ReviewCard[] {
  const cards: ReviewCard[] = [];
  for (const e of evidence) {
    if (e.kind !== 'record' || e.subject.type !== 'candidate' || e.lowDiscrimination || !allowed.has(e.subject.id)) continue;
    const parsed = parseVote(e.detail);
    const subject = describeSubject(catalog, e.subject);
    const statement = statements.get(e.questionId);
    if (!parsed || !subject.office || !statement) continue;
    const ref = [parsed.code, parsed.where].filter(Boolean).join(', ');
    const about = parsed.topic ?? lowerFirst(statement.replace(/\.$/, ''));
    cards.push({
      id: `vote:${e.id}`,
      kind: 'vote',
      candidateId: subject.id,
      about: `${subject.name}, candidato a ${OFFICE_BY_ID[subject.office].label.toLowerCase()}`,
      prompt: `Na votação sobre ${about} (${ref}), como ${subject.name} votou?`,
      quote: null,
      options: VOTE_OPTIONS,
      correct: parsed.vote === 'SIM' ? 0 : 1,
      explanation: `${e.detail} Na pergunta “${statement}”, esse voto conta como ${e.position > 0 ? 'a favor' : e.position < 0 ? 'contra' : 'meio-termo'}.`,
      source: e.source,
    });
  }
  return cards;
}

function pickOptions(correctId: string, pool: string[], catalog: Catalog, random: () => number): { options: ReviewOption[]; correct: number } | null {
  const distractors = shuffle(
    pool.filter((id) => id !== correctId),
    random,
  ).slice(0, 2);
  if (distractors.length < 2) return null;
  const ids = shuffle([correctId, ...distractors], random);
  const options = ids.map((id) => ({ label: describeSubject(catalog, { type: 'candidate', id }).name, candidateId: id }));
  return { options, correct: ids.indexOf(correctId) };
}

function sameOffice(allowed: Set<string>, catalog: Catalog, office: Office): string[] {
  return [...allowed].filter((id) => catalog.candidates.get(id)?.office === office);
}

function quoteCards(
  evidence: Evidence[],
  catalog: Catalog,
  allowed: Set<string>,
  statements: Map<string, string>,
  random: () => number,
): ReviewCard[] {
  const platform = evidence.filter((e) => e.kind === 'platform' && e.quote && e.subject.type === 'candidate' && allowed.has(e.subject.id));
  const cards: ReviewCard[] = [];
  for (const e of platform) {
    const subject = describeSubject(catalog, e.subject);
    if (!subject.office) continue;
    const saidTheSame = new Set(platform.filter((o) => o.quote === e.quote).map((o) => o.subject.id));
    const pool = sameOffice(allowed, catalog, subject.office).filter((id) => id === subject.id || !saidTheSame.has(id));
    const picked = pickOptions(subject.id, pool, catalog, random);
    if (!picked) continue;
    const fromPlan = e.source.label.toLowerCase().includes('plano de governo');
    const statement = statements.get(e.questionId);
    cards.push({
      id: `quote:${e.id}`,
      kind: 'quote',
      candidateId: subject.id,
      about: `Candidatos a ${OFFICE_BY_ID[subject.office].label.toLowerCase()}`,
      prompt: fromPlan ? 'Quem escreveu isto no plano de governo?' : 'Quem disse isto?',
      quote: e.quote as string,
      ...picked,
      explanation: `${subject.name}. ${e.detail}${statement ? ` O tema é: “${statement}”` : ''}`,
      source: e.source,
    });
  }
  return cards;
}

const ELECTED = /^(\d{4}): eleição para (.+?) \((.+?)\), pelo (.+?)\. Resultado no TSE: (Eleito[^.]*)\.$/;

export interface ParsedElection {
  year: string;
  office: string;
  place: string;
}

export function parseElection(text: string): ParsedElection | null {
  const m = ELECTED.exec(text);
  return m ? { year: m[1] as string, office: m[2] as string, place: m[3] as string } : null;
}

function electionKey(e: ParsedElection): string {
  return `${e.year}|${e.office}|${e.place}`;
}

function factCards(profiles: Profile[], catalog: Catalog, allowed: Set<string>, random: () => number): ReviewCard[] {
  const elections = new Map<string, { claim: Claim; parsed: ParsedElection }[]>();
  for (const p of profiles) {
    if (!allowed.has(p.candidateId)) continue;
    const rows = p.experience.map((claim) => ({ claim, parsed: parseElection(claim.text) })).filter((r) => r.parsed !== null);
    elections.set(p.candidateId, rows as { claim: Claim; parsed: ParsedElection }[]);
  }
  const cards: ReviewCard[] = [];
  for (const [id, rows] of elections) {
    const office = catalog.candidates.get(id)?.office;
    if (!office) continue;
    for (const { claim, parsed } of rows) {
      const key = electionKey(parsed);
      const pool = sameOffice(allowed, catalog, office).filter(
        (other) => other === id || !(elections.get(other) ?? []).some((r) => electionKey(r.parsed) === key),
      );
      const picked = pickOptions(id, pool, catalog, random);
      if (!picked) continue;
      const name = describeSubject(catalog, { type: 'candidate', id }).name;
      cards.push({
        id: `fact:${claim.checkId}`,
        kind: 'fact',
        candidateId: id,
        about: `Candidatos a ${OFFICE_BY_ID[office].label.toLowerCase()}`,
        prompt: `Quem foi eleito para ${parsed.office} (${parsed.place}) em ${parsed.year}?`,
        quote: null,
        ...picked,
        explanation: `${name}. ${claim.text}`,
        source: claim.source,
      });
    }
  }
  return cards;
}

/** Two evidence rows can record the same roll call or quote; the user should see it once. */
function uniqueCards(cards: ReviewCard[]): ReviewCard[] {
  const seen = new Set<string>();
  return cards.filter((c) => {
    const key = `${c.candidateId}|${c.prompt}|${c.quote ?? ''}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function interleave<T>(...lists: T[][]): T[] {
  const out: T[] = [];
  const longest = Math.max(0, ...lists.map((l) => l.length));
  for (let i = 0; i < longest; i += 1) for (const l of lists) if (l[i] !== undefined) out.push(l[i] as T);
  return out;
}

export interface ReviewInput {
  evidence: Evidence[];
  catalog: Catalog;
  profiles: Profile[];
  questions: Question[];
  seed: number;
  limit: number;
}

export function generateReview({ evidence, catalog, profiles, questions, seed, limit }: ReviewInput): ReviewCard[] {
  const random = seededRandom(seed);
  const allowed = quizCandidates(profiles, catalog);
  const statements = new Map(questions.map((q) => [q.id, q.statement]));
  const votes = shuffle(voteCards(evidence, catalog, allowed, statements), random);
  const quotes = shuffle(quoteCards(evidence, catalog, allowed, statements, random), random);
  const facts = shuffle(factCards(profiles, catalog, allowed, random), random);
  return uniqueCards(interleave(votes, quotes, facts)).slice(0, limit);
}

export type OptionState = 'idle' | 'right' | 'wrong';

export function optionState(index: number, picked: number | null, correct: number): OptionState {
  if (picked === null) return 'idle';
  if (index === correct) return 'right';
  if (index === picked) return 'wrong';
  return 'idle';
}

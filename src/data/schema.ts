export type Office =
  | 'presidente'
  | 'governador'
  | 'senador'
  | 'deputado_federal'
  | 'deputado_estadual'

export type Area = 'economia' | 'seguranca' | 'social' | 'ambiente'

export interface Source {
  url: string
  accessed: string
  label: string
}

export interface ElectedRecord {
  year: number
  office: string
  place: string
  party: string
}

export interface Candidate {
  id: string
  office: Office
  number: string
  ballotName: string
  party: string
  list: string
  listName: string
  runningMates: string[]
  status: string
  withdrawn: boolean
  elected: ElectedRecord[]
  planUrl?: string
  notice?: { text: string; sources: Source[] }
  planSource?: string
  source: Source
}

export interface Question {
  id: string
  area: Area
  offices: Office[]
  statement: string
  context: string
  sources: Source[]
  /** Optional nuanced answer scale; values map onto the same -1..1 stance axis. */
  options?: { label: string; value: -1 | -0.5 | 0 | 0.5 | 1 }[]
}

export type EvidenceKind = 'record' | 'platform'

export type Position = -1 | 0 | 1

export interface Evidence {
  id: string
  subject: { type: 'candidate' | 'list'; id: string }
  questionId: string
  kind: EvidenceKind
  position: Position
  detail: string
  quote?: string
  page?: number
  date: string
  source: Source
  checkId: string
  lowDiscrimination: boolean
}

export interface Poll {
  id: string
  office: Office
  institute: string
  fieldStart: string
  fieldEnd: string
  sample: number
  marginPp: number
  registration: string
  results: { label: string; pct: number }[]
  source: Source
  verified: 'tse' | 'press'
}

export interface Meta {
  builtAt: string
  electionDate: string
  evidence: number
  questions: number
}

/** One checkable sentence: `support` must appear verbatim (normalized) in `source`. */
export interface Claim {
  text: string
  support: string
  source: Source
  checkId: string
}

/** Shown before the user answers. Arguments are attributed to who makes them. */
export interface Explainer {
  questionId: string
  whatItIs: Claim[]
  inPractice: Claim[]
  argsFor: Claim[]
  argsAgainst: Claim[]
  nuance: Claim[]
}

export type Axis = 'economico' | 'social'

/** Method, not fact: which axis a question feeds and which pole "concordo" points to. */
export interface AxisAssignment {
  questionId: string
  axis: Axis
  direction: 1 | -1
  rationale: string
}

export interface Profile {
  candidateId: string
  office: Office
  pollRank: number | null
  presents: Claim[]
  experience: Claim[]
  proposals: Claim[]
  defends: string[]
}

export interface CountryStance {
  id: string
  country: string
  questionId: string
  position: Position
  detail: string
  support: string
  source: Source
  checkId: string
}

export type ControversyCategory =
  | 'justica'
  | 'investigacao'
  | 'familia'
  | 'declaracao'
  | 'proposta'
  | 'patrimonio'
  | 'experiencia'

/** Documented facts only. `status` states the exact legal situation; `response` is the candidate's published reply. */
export interface Controversy {
  id: string
  candidateId: string
  category: ControversyCategory
  title: string
  status: string
  date: string
  claims: Claim[]
  response: Claim[]
}

export interface Portrait {
  candidateId: string
  file: string
  photoSource: Source
}

export interface Round2Finalist {
  candidateId: string
  number: string
  ballotName: string
  pctBrasil: string
  pctParaiba: string
}

export interface Round2Office {
  office: Office
  status: 'runoff' | 'decided'
  finalists?: Round2Finalist[]
  winner?: { candidateId: string; number: string; ballotName: string; pct: string } | null
  sources: Source[]
}

export interface Round2 {
  date: string
  dateSource: Source
  offices: Round2Office[]
}

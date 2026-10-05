import type {
  AxisAssignment,
  Candidate,
  CountryStance,
  Evidence,
  Explainer,
  Meta,
  Poll,
  Portrait,
  Profile,
  Question,
  Controversy,
  Round2,
  Round1,
  Endorsement,
} from './schema';
import axesJson from './axes.json';
import candidatesJson from './candidates.json';
import countriesJson from './countries.json';
import evidenceJson from './evidence.json';
import explainersJson from './explainers.json';
import metaJson from './meta.json';
import pollsJson from './polls.json';
import profilesJson from './profiles.json';
import questionsJson from './questions.json';
import controversiesJson from './controversies.json';
import portraitsJson from './portraits.json';
import round2Json from './round2.json';
import round1Json from './round1.json';
import endorsementsJson from './endorsements.json';
import polls2Json from './polls2.json';

export const candidates = candidatesJson as Candidate[];
export const evidence = evidenceJson as Evidence[];
export const questions = questionsJson as Question[];
export const polls = pollsJson as Poll[];
export const meta = metaJson as Meta;
export const explainers = explainersJson as unknown as Explainer[];
export const axes = axesJson as unknown as AxisAssignment[];
export const profiles = profilesJson as unknown as Profile[];
export const countries = countriesJson as unknown as CountryStance[];
export const controversies = controversiesJson as unknown as Controversy[];
export const portraits = portraitsJson as unknown as Portrait[];
export const round2 = round2Json as unknown as Round2;
export const round1 = round1Json as unknown as Round1;
export const endorsements = endorsementsJson as unknown as Endorsement[];
export const polls2 = polls2Json as Poll[];

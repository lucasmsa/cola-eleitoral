import type { Area, Office } from '@/data/schema';

export const ELECTION_DATE = '2026-10-04';
export const ELECTION_LABEL = '4 de outubro';

export interface OfficeConfig {
  id: Office;
  label: string;
  tab: string;
  digits: number;
  seats: number;
  listFirst: boolean;
}

export const OFFICES: OfficeConfig[] = [
  { id: 'presidente', label: 'Presidente', tab: 'Presidente', digits: 2, seats: 1, listFirst: false },
  { id: 'governador', label: 'Governador', tab: 'Governador', digits: 2, seats: 1, listFirst: false },
  { id: 'senador', label: 'Senador', tab: 'Senado (escolha 2)', digits: 3, seats: 2, listFirst: false },
  { id: 'deputado_federal', label: 'Deputado federal', tab: 'Deputado federal', digits: 4, seats: 12, listFirst: true },
  { id: 'deputado_estadual', label: 'Deputado estadual', tab: 'Deputado estadual', digits: 5, seats: 36, listFirst: true },
];

export const OFFICE_BY_ID = Object.fromEntries(OFFICES.map((o) => [o.id, o])) as Record<Office, OfficeConfig>;

export type ColaSlotId =
  | 'deputado_federal'
  | 'deputado_estadual'
  | 'senador_1'
  | 'senador_2'
  | 'governador'
  | 'presidente';

export interface ColaSlot {
  id: ColaSlotId;
  office: Office;
  label: string;
  digits: number;
  allowsLegenda: boolean;
}

export const COLA_SLOTS: ColaSlot[] = [
  { id: 'deputado_federal', office: 'deputado_federal', label: 'Deputado federal', digits: 4, allowsLegenda: true },
  { id: 'deputado_estadual', office: 'deputado_estadual', label: 'Deputado estadual', digits: 5, allowsLegenda: true },
  { id: 'senador_1', office: 'senador', label: 'Senador, 1ª vaga', digits: 3, allowsLegenda: false },
  { id: 'senador_2', office: 'senador', label: 'Senador, 2ª vaga', digits: 3, allowsLegenda: false },
  { id: 'governador', office: 'governador', label: 'Governador', digits: 2, allowsLegenda: false },
  { id: 'presidente', office: 'presidente', label: 'Presidente', digits: 2, allowsLegenda: false },
];

export interface AreaConfig {
  id: Area;
  label: string;
  blurb: string;
}

export const AREAS: AreaConfig[] = [
  { id: 'economia', label: 'Economia', blurb: 'Impostos, gasto público, estatais e Banco Central.' },
  { id: 'seguranca', label: 'Segurança e justiça', blurb: 'Presos, drogas, 8 de janeiro e foro dos parlamentares.' },
  { id: 'social', label: 'Social e direitos', blurb: 'Terras indígenas, aborto e cotas.' },
  { id: 'ambiente', label: 'Meio ambiente e energia', blurb: 'Licenciamento, petróleo e agrotóxicos.' },
];

export const PB_UNIT_LABEL = 'Paraíba';

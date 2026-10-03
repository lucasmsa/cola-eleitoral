import type { Controversy, ControversyCategory } from '@/data/schema';

export const CATEGORY_LABEL: Record<ControversyCategory, string> = {
  justica: 'Justiça',
  investigacao: 'Investigação',
  familia: 'Família',
  declaracao: 'Declaração',
  proposta: 'Proposta',
  patrimonio: 'Patrimônio',
  experiencia: 'Experiência',
};

export function controversiesOf(all: Controversy[], candidateId: string): Controversy[] {
  return all.filter((c) => c.candidateId === candidateId).sort((a, b) => b.date.localeCompare(a.date));
}

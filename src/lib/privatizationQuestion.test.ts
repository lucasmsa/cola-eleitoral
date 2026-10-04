import { describe, expect, it } from 'vitest';
import draft from '../../pipeline/questions.draft.json';
import questions from '../data/questions.json';

describe('privatization question', () => {
  const question = questions.find((item) => item.id === 'eco-privatizacao');

  it('keeps the source and shipped statement general, without calling Eletrobras a current state-owned company', () => {
    const statement = 'Empresas estatais devem ser privatizadas.';
    expect(question?.statement).toBe(statement);
    expect(draft.questions.find((item) => item.id === 'eco-privatizacao')?.statement).toBe(statement);
  });

  it('preserves the existing answer scale and the historical Eletrobras vote references', () => {
    expect(question?.options).toEqual([
      { label: 'Reestatizar o que foi privatizado', value: -1 },
      { label: 'Manter as estatais que existem hoje', value: -0.5 },
      { label: 'Meio-termo, caso a caso', value: 0 },
      { label: 'Privatizar algumas, mantendo as estratégicas', value: 0.5 },
      { label: 'Privatizar a maioria das estatais', value: 1 },
    ]);
    expect(question?.context).toContain('MP 1.031/2021 (privatização da Eletrobras)');
    expect(question?.sources.map((source) => source.url)).toContain(
      'https://dadosabertos.camara.leg.br/api/v2/votacoes/2270789-73',
    );
  });
});

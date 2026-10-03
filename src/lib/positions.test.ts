import { describe, expect, it } from 'vitest';
import { STANCES } from '@/config/answers';
import { answerLabel, stanceOptionsFor } from './positions';

describe('stanceOptionsFor', () => {
  it('uses the generic five stances when the question has no own scale', () => {
    expect(stanceOptionsFor({}, STANCES)).toBe(STANCES);
    expect(stanceOptionsFor({ options: [{ value: 1, label: 'Só uma' }] }, STANCES)).toBe(STANCES);
  });

  it('uses the question scale ordered from -1 to 1, keeping the same stance numbers', () => {
    const options = stanceOptionsFor(
      {
        options: [
          { value: 1, label: 'Ampliar o acesso a armas' },
          { value: -1, label: 'Restringir mais' },
          { value: 0, label: 'Manter as regras atuais' },
        ],
      },
      STANCES,
    );
    expect(options.map((o) => o.value)).toEqual([-1, 0, 1]);
    expect(options[0]?.label).toBe('Restringir mais');
  });
});

describe('answerLabel', () => {
  it('names the answer with the question scale when there is one', () => {
    expect(answerLabel({ options: [{ value: 0, label: 'Manter as regras atuais' }] }, 0)).toBe('Manter as regras atuais');
    expect(answerLabel(undefined, -0.5)).toBe('Discordo');
  });
});

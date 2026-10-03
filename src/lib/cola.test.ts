import { describe, expect, it } from 'vitest';
import { COLA_SLOTS } from '@/config/election';
import { cand } from '@/test/fixtures';
import { listParties, lookupSlot, sanitizeDigits } from './cola';

const candidates = [
  cand('deputado_federal-1345', { party: 'PT', list: 'FE' }),
  cand('deputado_federal-6565', { party: 'PC do B', list: 'FE' }),
  cand('deputado_federal-2222', { party: 'PL', list: 'PL' }),
  cand('senador-155'),
];
const slot = (id: string) => COLA_SLOTS.find((s) => s.id === id)!;

describe('lookupSlot', () => {
  it('finds a candidate by the full number in the slot office only', () => {
    const r = lookupSlot(slot('senador_1'), { kind: 'number', digits: '155' }, candidates);
    expect(r.status).toBe('candidate');
    expect(lookupSlot(slot('deputado_federal'), { kind: 'number', digits: '1555' }, candidates).status).toBe('not-found');
  });

  it('accepts a 2-digit legenda vote only for deputados', () => {
    const r = lookupSlot(slot('deputado_federal'), { kind: 'number', digits: '13' }, candidates);
    expect(r).toEqual({ status: 'legenda', partyNumber: '13', party: 'PT' });
    expect(lookupSlot(slot('deputado_federal'), { kind: 'number', digits: '99' }, candidates).status).toBe('not-found');
    expect(lookupSlot(slot('senador_1'), { kind: 'number', digits: '15' }, candidates).status).toBe('incomplete');
  });

  it('reports empty, incomplete and branco', () => {
    expect(lookupSlot(slot('presidente'), undefined, candidates).status).toBe('empty');
    expect(lookupSlot(slot('deputado_federal'), { kind: 'number', digits: '134' }, candidates).status).toBe('incomplete');
    expect(lookupSlot(slot('presidente'), { kind: 'branco' }, candidates).status).toBe('branco');
  });
});

describe('helpers', () => {
  it('keeps digits only, up to the slot size', () => {
    expect(sanitizeDigits('1a3-45', 4)).toBe('1345');
    expect(sanitizeDigits('123456', 5)).toBe('12345');
  });

  it('lists the party numbers inside a federation', () => {
    expect(listParties('FE', 'deputado_federal', candidates)).toEqual([
      { number: '13', party: 'PT' },
      { number: '65', party: 'PC do B' },
    ]);
  });
});

describe('colaRowName', () => {
  it('prints the ballot name, the legenda party or BRANCO', async () => {
    const { colaRowName } = await import('./colaView');
    expect(colaRowName({ status: 'candidate', candidate: cand('senador-155', { ballotName: 'VENEZIANO' }) })).toBe('Veneziano');
    expect(colaRowName({ status: 'legenda', partyNumber: '13', party: 'PT' })).toBe('legenda PT');
    expect(colaRowName({ status: 'branco' })).toBe('BRANCO');
    expect(colaRowName({ status: 'empty' })).toBe('');
  });
});

describe('colaStatus', () => {
  it('shows the name like the urna, or explains what is wrong', async () => {
    const { colaStatus } = await import('./colaStatus');
    expect(colaStatus({ status: 'candidate', candidate: cand('senador-155', { ballotName: 'VENEZIANO', party: 'MDB' }) }, 3)).toEqual({
      kind: 'ok',
      text: 'Veneziano, MDB',
    });
    expect(colaStatus({ status: 'not-found' }, 3)).toEqual({ kind: 'warn', text: 'Número não encontrado para este cargo' });
    expect(colaStatus({ status: 'incomplete' }, 4).text).toBe('Faltam dígitos: este cargo tem 4');
  });
});

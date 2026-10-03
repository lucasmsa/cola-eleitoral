import { describe, expect, it } from 'vitest';
import { cand, ev } from '@/test/fixtures';
import { buildCatalog, evidenceBadge, groupEvidence } from './subjects';
import { titleCase } from './text';

describe('titleCase', () => {
  it('keeps Portuguese particles lowercase', () => {
    expect(titleCase('CÍCERO LUCENA DA SILVA')).toBe('Cícero Lucena da Silva');
  });
});

describe('evidence helpers', () => {
  const catalog = buildCatalog([cand('presidente-13', { ballotName: 'LULA' }), cand('senador-155', { ballotName: 'VENEZIANO' })]);

  it('badges votes, executive acts, orientations and declarations', () => {
    expect(evidenceBadge(ev('senador-155', 'q'))).toBe('Votou');
    expect(evidenceBadge(ev('presidente-13', 'q', { detail: 'Vetou o artigo 3.' }))).toBe('Sancionou ou vetou');
    expect(evidenceBadge(ev('PL', 'q', { subject: { type: 'list', id: 'PL' } }))).toBe('Orientou');
    expect(evidenceBadge(ev('presidente-13', 'q', { kind: 'platform' }))).toBe('Declarou');
  });

  it('groups evidence by office in ballot order, lists last', () => {
    const groups = groupEvidence(catalog, [
      ev('PL', 'q', { subject: { type: 'list', id: 'PL' } }),
      ev('senador-155', 'q'),
      ev('presidente-13', 'q'),
    ]);
    expect(groups.map((g) => g.key)).toEqual(['presidente', 'senador', 'list']);
  });

  it('collects several facts about the same person under one entry', () => {
    const groups = groupEvidence(catalog, [ev('senador-155', 'q', { id: 'a' }), ev('senador-155', 'q', { id: 'b' })]);
    expect(groups[0]?.items).toHaveLength(1);
    expect(groups[0]?.items[0]?.evidence.map((e) => e.id)).toEqual(['a', 'b']);
  });

  it('uses the readable federation label', () => {
    const c = buildCatalog([cand('deputado_federal-5050', { list: '50-PSOL/18-REDE', listName: 'Federação Psol Rede' })]);
    expect(c.listNames.get('50-PSOL/18-REDE')).toBe('Federação PSOL REDE (PSOL, Rede)');
  });
});

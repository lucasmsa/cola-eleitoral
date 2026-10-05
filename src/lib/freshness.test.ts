import { describe, expect, it } from 'vitest';
import { dataFreshness, newestStamp, stampsIn } from './freshness';

describe('stampsIn', () => {
  it('finds TSE generation stamps in labels and generated fields', () => {
    const data = {
      a: { source: { generated: '04/10/2026 23:23' } },
      b: [{ label: 'TSE, presidente no Brasil, gerado em 05/10/2026 às 12:51:47' }],
      c: { label: 'Imprensa, sem data' },
    };
    expect(stampsIn(data)).toEqual(['04/10/2026 23:23', '05/10/2026 12:51']);
  });
});

describe('newestStamp', () => {
  it('compares by date then time, not as text', () => {
    expect(newestStamp(['30/09/2026 19:30', '04/10/2026 08:30', '03/10/2026 12:30'])).toBe('04/10/2026 08:30');
    expect(newestStamp([])).toBeNull();
  });
});

describe('dataFreshness', () => {
  it('reports each dataset with its own date', () => {
    const f = dataFreshness({
      candidates: [{ notice: { sources: [{ label: 'TSE, consulta_cand_complementar_2026_PB.csv, gerado em 04/10/2026 08:30' }] } }],
      results: [{ source: { generated: '04/10/2026 23:23' } }, { sources: [{ label: 'TSE, gerado em 05/10/2026 às 12:51:44' }] }],
      builtAt: '2026-10-05',
      polls: [{ office: 'senador', institute: 'Quaest', fieldStart: '2026-10-02', fieldEnd: '2026-10-03' }],
      officeLabel: (o) => (o === 'senador' ? 'Senado PB' : o),
    });
    expect(f).toEqual({
      candidatos: '04/10/2026 08:30',
      resultados: '05/10/2026 12:51',
      evidencias: '05/10/2026',
      pesquisas: [{ office: 'Senado PB', institute: 'Quaest', field: '02/10/2026 a 03/10/2026' }],
    });
  });
});

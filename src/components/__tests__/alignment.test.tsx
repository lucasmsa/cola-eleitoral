import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import type { Dot } from '@/lib/chart';
import { AlignmentChart } from '../alignment/AlignmentChart';

const dot = (id: string, label: string, kind: Dot['kind']): Dot => ({
  id,
  label,
  detail: '',
  kind,
  placement: { x: { value: 0.2, n: 4 }, y: { value: -0.4, n: 3 }, visible: true },
  cx: 300,
  cy: 320,
  labelDy: 0,
  labelSide: 'right',
});

describe('AlignmentChart', () => {
  it('draws the poles and one focusable mark per dot, naming how many questions back it', () => {
    render(<AlignmentChart dots={[dot('voce', 'Você', 'voce'), dot('pais:Chile', 'Chile', 'pais')]} focusedId={null} onFocus={() => {}} />);
    for (const pole of ['mais Estado', 'mais mercado', 'conservador', 'progressista']) expect(screen.getByText(new RegExp(pole))).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Chile: 4 perguntas no eixo econômico, 3 no de costumes' })).toBeInTheDocument();
    expect(screen.getByText('Você')).toBeInTheDocument();
  });
});

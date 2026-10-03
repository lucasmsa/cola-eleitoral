import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it } from 'vitest';
import { useAnswersStore } from '@/stores/answers';
import { ColaScreen } from '../cola/ColaScreen';

describe('cola manual entry', () => {
  beforeEach(() => useAnswersStore.getState().resetAll());

  it('looks the number up like the urna and fills the card', async () => {
    const user = userEvent.setup();
    render(<ColaScreen />);
    const senator = screen.getByLabelText(/Senador, 1ª vaga/);
    await user.type(senator, '155');
    expect(screen.getByText('Veneziano, MDB')).toBeInTheDocument();
    expect(useAnswersStore.getState().cola.senador_1).toEqual({ kind: 'number', digits: '155' });
    const card = screen.getAllByTestId('cola-card')[0]!;
    expect(within(card).getByText('Veneziano')).toBeInTheDocument();
  });

  it('flags unknown numbers, accepts legenda for deputados and branco', async () => {
    const user = userEvent.setup();
    render(<ColaScreen />);
    await user.type(screen.getByLabelText(/Governador/), '99');
    expect(screen.getByText('Número não encontrado para este cargo')).toBeInTheDocument();

    await user.type(screen.getByLabelText(/Deputado federal/), '13');
    expect(screen.getByText('Legenda do PT')).toBeInTheDocument();

    const president = screen.getByLabelText(/Presidente/).closest('li')!;
    await user.click(within(president).getByRole('button', { name: 'Branco' }));
    expect(within(president).getByText('Voto em branco')).toBeInTheDocument();
  });

  it('keeps digits only and warns when both senate slots hold the same number', async () => {
    const user = userEvent.setup();
    render(<ColaScreen />);
    await user.type(screen.getByLabelText(/Senador, 1ª vaga/), '1a5b5');
    await user.type(screen.getByLabelText(/Senador, 2ª vaga/), '155');
    expect(useAnswersStore.getState().cola.senador_1).toEqual({ kind: 'number', digits: '155' });
    expect(screen.getByText(/O mesmo número está nas duas vagas/)).toBeInTheDocument();
  });
});

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it } from 'vitest';
import { questions } from '@/data';
import { buildUnits } from '@/lib/lessons';
import { useAnswersStore } from '@/stores/answers';
import { LessonScreen } from '../lesson/LessonScreen';

const unit = buildUnits(questions)[0]!;

describe('lesson flow', () => {
  beforeEach(() => useAnswersStore.getState().resetAll());

  it('records stance and importance without showing any candidate position, then moves on', async () => {
    const user = userEvent.setup();
    render(<LessonScreen unitId={unit.id} />);
    expect(screen.getByRole('heading', { level: 1, name: unit.questions[0]!.statement })).toBeInTheDocument();
    expect(screen.getByText('Entenda antes de responder')).toBeInTheDocument();

    const confirm = screen.getByRole('button', { name: 'Confirmar' });
    expect(confirm).toBeDisabled();
    await user.click(screen.getByRole('radio', { name: 'Concordo' }));
    await user.click(screen.getByRole('radio', { name: 'Muito' }));
    await user.click(confirm);

    expect(useAnswersStore.getState().answers[unit.questions[0]!.id]).toEqual({ stance: 0.5, importance: 2 });
    expect(await screen.findByText('Resposta registrada.')).toBeInTheDocument();
    expect(screen.queryByText(/Votou (SIM|NÃO)/)).not.toBeInTheDocument();
    expect(screen.queryByText('A favor')).not.toBeInTheDocument();
    expect(screen.queryByText('Contra')).not.toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'Próxima pergunta' }));
    expect(await screen.findByRole('heading', { level: 1, name: unit.questions[1]!.statement })).toBeInTheDocument();
  });

  it('stores "Não sei" as a skip', async () => {
    const user = userEvent.setup();
    render(<LessonScreen unitId={unit.id} />);
    await user.click(screen.getByRole('button', { name: 'Não sei' }));
    expect(useAnswersStore.getState().answers[unit.questions[0]!.id]).toBe('skip');
    expect(await screen.findByText(/fica fora da conta/)).toBeInTheDocument();
  });

  it('goes back to the previous question with its answer preselected and editable', async () => {
    const user = userEvent.setup();
    render(<LessonScreen unitId={unit.id} />);
    expect(screen.queryByRole('button', { name: 'Voltar' })).not.toBeInTheDocument();
    await user.click(screen.getByRole('radio', { name: 'Concordo' }));
    await user.click(screen.getByRole('radio', { name: 'Muito' }));
    await user.click(screen.getByRole('button', { name: 'Confirmar' }));
    await user.click(await screen.findByRole('button', { name: 'Próxima pergunta' }));

    await user.click(await screen.findByRole('button', { name: 'Voltar' }));
    expect(await screen.findByRole('heading', { level: 1, name: unit.questions[0]!.statement })).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: 'Concordo' })).toBeChecked();
    expect(screen.getByRole('radio', { name: 'Muito' })).toBeChecked();

    await user.click(screen.getByRole('radio', { name: 'Discordo' }));
    await user.click(screen.getByRole('button', { name: 'Confirmar' }));
    expect(useAnswersStore.getState().answers[unit.questions[0]!.id]).toEqual({ stance: -0.5, importance: 2 });
  });
});

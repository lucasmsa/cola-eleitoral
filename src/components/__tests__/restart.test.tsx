import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it } from 'vitest';
import { useAnswersStore } from '@/stores/answers';
import { useScreenStore } from '@/stores/screen';
import { RestartQuiz } from '../shell/RestartQuiz';

describe('restart quiz', () => {
  beforeEach(() => {
    useAnswersStore.getState().resetAll();
    useAnswersStore.getState().setAnswer('q1', { stance: 1, importance: 2 });
    useAnswersStore.getState().setCola('presidente', { kind: 'number', digits: '13' });
    useScreenStore.getState().go({ name: 'results', step: 'alinhamento' });
  });

  it('asks inline first and keeps everything when cancelled', async () => {
    const user = userEvent.setup();
    render(<RestartQuiz />);
    await user.click(screen.getByRole('button', { name: 'Recomeçar o quiz do zero' }));
    expect(await screen.findByRole('alertdialog')).toHaveTextContent('Isso apaga todas as suas respostas');
    await user.click(screen.getByRole('button', { name: 'Cancelar' }));
    expect(useAnswersStore.getState().answers.q1).toEqual({ stance: 1, importance: 2 });
  });

  it('clears answers and cola and goes home when confirmed', async () => {
    const user = userEvent.setup();
    render(<RestartQuiz />);
    await user.click(screen.getByRole('button', { name: 'Recomeçar o quiz do zero' }));
    await user.click(await screen.findByRole('button', { name: 'Sim, apagar e recomeçar' }));
    expect(useAnswersStore.getState().answers).toEqual({});
    expect(useAnswersStore.getState().cola).toEqual({});
    expect(useScreenStore.getState().screen).toEqual({ name: 'home' });
  });
});

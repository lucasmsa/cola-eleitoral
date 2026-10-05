import { act, renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { useScreenStore } from '@/stores/screen';
import { useTurnoStore } from '@/stores/turno';
import { useTurno } from '../useTurno';

describe('useTurno', () => {
  beforeEach(() => {
    useTurnoStore.setState({ turno: 2 });
    useScreenStore.setState({ screen: { name: 'home' } });
  });

  it('starts on the 2nd round with its own nav', () => {
    const { result } = renderHook(() => useTurno());
    expect(result.current.turno).toBe(2);
    expect(result.current.links.map((l) => l.key)).toEqual(['home', 'round2', 'cola2']);
  });

  it('sends the user home when the current screen does not exist in the other turno', () => {
    useScreenStore.setState({ screen: { name: 'round2' } });
    const { result } = renderHook(() => useTurno());
    act(() => result.current.choose(1));
    expect(useTurnoStore.getState().turno).toBe(1);
    expect(useScreenStore.getState().screen.name).toBe('home');
    expect(result.current.links.map((l) => l.key)).toContain('round1');
  });

  it('keeps a lesson open across the switch and persists the choice', () => {
    useScreenStore.setState({ screen: { name: 'lesson', unitId: 'economia' } });
    const { result } = renderHook(() => useTurno());
    act(() => result.current.choose(1));
    expect(useScreenStore.getState().screen.name).toBe('lesson');
    expect(JSON.parse(localStorage.getItem('cola-eleitoral:turno') ?? '{}').state.turno).toBe(1);
  });
});

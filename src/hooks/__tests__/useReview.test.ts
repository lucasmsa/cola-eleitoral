import { act, renderHook } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { useReview } from '../useReview';

describe('useReview back navigation', () => {
  it('returns to the previous card with its pick kept and locked', () => {
    const { result } = renderHook(() => useReview());
    act(() => result.current.start());
    expect(result.current.canGoBack).toBe(false);
    const first = result.current.card;
    act(() => result.current.pick(0));
    act(() => result.current.next());
    expect(result.current.position).toBe(2);
    expect(result.current.picked).toBeNull();

    act(() => result.current.back());
    expect(result.current.position).toBe(1);
    expect(result.current.card).toBe(first);
    expect(result.current.picked).toBe(0);
    act(() => result.current.pick(1));
    expect(result.current.picked).toBe(0);
  });
});

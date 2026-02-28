import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useLoadingState } from '../hooks/useLoadingState';

describe('useLoadingState', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  it('initializes with isLoading = false', () => {
    const { result } = renderHook(() => useLoadingState());
    expect(result.current.isLoading).toBe(false);
  });

  it('sets isLoading to true immediately when setLoading(true)', () => {
    const { result } = renderHook(() => useLoadingState());
    act(() => {
      result.current.setLoading(true);
    });
    expect(result.current.isLoading).toBe(true);
  });

  it('respects minimum loading time of 300ms by default', async () => {
    const { result } = renderHook(() => useLoadingState());

    act(() => {
      result.current.setLoading(true);
    });
    expect(result.current.isLoading).toBe(true);

    // Advance 100ms (less than 300ms)
    act(() => {
      vi.advanceTimersByTime(100);
    });

    // Call setLoading(false) at 100ms
    act(() => {
      result.current.setLoading(false);
    });

    // Should still be loading
    expect(result.current.isLoading).toBe(true);

    // Advance 150ms more (total 250ms)
    act(() => {
      vi.advanceTimersByTime(150);
    });

    // Should still be loading
    expect(result.current.isLoading).toBe(true);

    // Advance 50ms more (total 300ms)
    act(() => {
      vi.advanceTimersByTime(50);
    });

    // Now should be false
    expect(result.current.isLoading).toBe(false);
  });

  it('does not delay when setLoading(false) is called after 300ms+', async () => {
    const { result } = renderHook(() => useLoadingState());

    act(() => {
      result.current.setLoading(true);
    });

    // Advance 400ms (more than 300ms minimum)
    act(() => {
      vi.advanceTimersByTime(400);
    });

    // setLoading(false) should complete immediately
    act(() => {
      result.current.setLoading(false);
    });

    expect(result.current.isLoading).toBe(false);
  });

  it('allows custom minLoadingTime', async () => {
    const { result } = renderHook(() => useLoadingState(500));

    act(() => {
      result.current.setLoading(true);
    });

    // Advance 300ms (less than 500ms)
    act(() => {
      vi.advanceTimersByTime(300);
    });

    act(() => {
      result.current.setLoading(false);
    });

    // Should still be loading after 300ms
    expect(result.current.isLoading).toBe(true);

    // Advance 150ms more (total 450ms)
    act(() => {
      vi.advanceTimersByTime(150);
    });

    // Should still be loading (450 < 500)
    expect(result.current.isLoading).toBe(true);

    // Advance 50ms more (total 500ms)
    act(() => {
      vi.advanceTimersByTime(50);
    });

    // Now should be false
    expect(result.current.isLoading).toBe(false);
  });

  it('handles rapid loading state changes', () => {
    const { result } = renderHook(() => useLoadingState());

    act(() => {
      result.current.setLoading(true);
      result.current.setLoading(false);
      result.current.setLoading(true);
    });

    expect(result.current.isLoading).toBe(true);
  });

  afterEach(() => {
    vi.useRealTimers();
  });
});

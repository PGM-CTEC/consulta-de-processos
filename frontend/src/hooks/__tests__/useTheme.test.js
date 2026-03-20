import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import { useSettingsStore } from '../../stores/settingsStore';
import { useTheme } from '../useTheme';

describe('useTheme', () => {
  beforeEach(() => {
    // Reset store e DOM
    useSettingsStore.setState({ theme: 'light' });
    document.documentElement.classList.remove('dark');
  });

  it('retorna theme light por padrão', () => {
    const { result } = renderHook(() => useTheme());
    expect(result.current.theme).toBe('light');
    expect(result.current.isDark).toBe(false);
  });

  it('toggleTheme muda para dark e aplica classe no <html>', () => {
    const { result } = renderHook(() => useTheme());
    act(() => { result.current.toggleTheme(); });
    expect(result.current.theme).toBe('dark');
    expect(result.current.isDark).toBe(true);
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('toggleTheme de dark para light remove classe do <html>', () => {
    useSettingsStore.setState({ theme: 'dark' });
    const { result } = renderHook(() => useTheme());
    act(() => { result.current.toggleTheme(); });
    expect(result.current.theme).toBe('light');
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });

  it('aplica classe dark no mount se theme=dark no store', () => {
    useSettingsStore.setState({ theme: 'dark' });
    renderHook(() => useTheme());
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });
});

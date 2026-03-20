import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from '../App';

vi.mock('../hooks/useLabels', () => ({
  useLabels: () => ({
    labels: {
      app: { title: 'Consulta Processual', subtitle: 'DataJud', statusOnline: 'Online', footerText: '' },
      nav: { single: 'Consulta Individual', bulk: 'Busca em Lote', analytics: 'Analytics / BI', history: 'Histórico' },
      home: { heroTitle: '', heroHighlight: '', heroSubtitle: '' },
      search: { placeholder: '', button: 'Consultar', loading: '', success: '', error: '' },
    },
    loading: false,
  }),
}));

describe('App — navegação', () => {
  it('não exibe aba Performance', () => {
    render(<App />);
    expect(screen.queryByRole('tab', { name: /performance/i })).toBeNull();
  });

  it('não exibe aba Configurações', () => {
    render(<App />);
    expect(screen.queryByRole('tab', { name: /configurações/i })).toBeNull();
  });

  it('exibe as 4 abas corretas', () => {
    render(<App />);
    expect(screen.getByRole('tab', { name: /consulta individual/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /busca em lote/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /analytics/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /histórico/i })).toBeInTheDocument();
  });

  it('exibe botão de toggle de tema', () => {
    render(<App />);
    expect(screen.getByRole('button', { name: /alternar tema/i })).toBeInTheDocument();
  });
});

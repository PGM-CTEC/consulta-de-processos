import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import PhasesReferenceModal from '../PhasesReferenceModal';

describe('PhasesReferenceModal', () => {
  it('renderiza o título das fases', () => {
    render(<PhasesReferenceModal onClose={() => {}} />);
    expect(screen.getByRole('heading', { name: /^fases processuais$/i, level: 2 })).toBeInTheDocument();
  });

  it('chama onClose ao clicar no botão fechar', () => {
    const onClose = vi.fn();
    render(<PhasesReferenceModal onClose={onClose} />);
    fireEvent.click(screen.getByRole('button', { name: /fechar/i }));
    expect(onClose).toHaveBeenCalledOnce();
  });

  it('fecha ao pressionar Escape', () => {
    const onClose = vi.fn();
    render(<PhasesReferenceModal onClose={onClose} />);
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(onClose).toHaveBeenCalledOnce();
  });

  it('tem atributos de acessibilidade corretos', () => {
    render(<PhasesReferenceModal onClose={() => {}} />);
    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-labelledby');
  });
});

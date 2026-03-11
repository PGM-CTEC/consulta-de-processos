/* eslint-disable no-undef */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import PhaseEditModal from '../components/PhaseEditModal';
import * as toastModule from 'react-hot-toast';

vi.mock('react-hot-toast', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

global.fetch = vi.fn();

describe('PhaseEditModal', () => {
  const mockOnClose = vi.fn();
  const mockOnSave = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch.mockClear();
  });

  it('não renderiza quando isOpen é false', () => {
    const { container } = render(
      <PhaseEditModal
        isOpen={false}
        processNumber="0123456-78.2020.8.19.0001"
        currentPhase="02"
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renderiza modal quando isOpen é true', () => {
    render(
      <PhaseEditModal
        isOpen={true}
        processNumber="0123456-78.2020.8.19.0001"
        currentPhase="02"
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );
    expect(screen.getByText('Editar Fase')).toBeInTheDocument();
    expect(screen.getByText(/0123456-78.2020.8.19.0001/)).toBeInTheDocument();
  });

  it('exibe erro se tentar salvar sem motivo', async () => {
    render(
      <PhaseEditModal
        isOpen={true}
        processNumber="0123456-78.2020.8.19.0001"
        currentPhase="02"
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    // O botão deveria estar desabilitado inicialmente
    const saveButton = screen.getByRole('button', { name: /Salvar Correção/i });
    expect(saveButton).toBeDisabled();

    // Colocamos um espaço vazio e tentamos salvar
    const textarea = screen.getByPlaceholderText(/Ex: Processo foi remetido/);
    fireEvent.change(textarea, { target: { value: '   ' } });

    // Botão continua desabilitado para espaços em branco
    expect(saveButton).toBeDisabled();
  });

  it('desabilita botão de salvar quando motivo está vazio', () => {
    render(
      <PhaseEditModal
        isOpen={true}
        processNumber="0123456-78.2020.8.19.0001"
        currentPhase="02"
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    const saveButton = screen.getByRole('button', { name: /Salvar Correção/i });
    expect(saveButton).toBeDisabled();
  });

  it('habilita botão de salvar quando motivo é fornecido', async () => {
    render(
      <PhaseEditModal
        isOpen={true}
        processNumber="0123456-78.2020.8.19.0001"
        currentPhase="02"
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    const textarea = screen.getByPlaceholderText(/Ex: Processo foi remetido/);
    fireEvent.change(textarea, { target: { value: 'Encontrado trânsito em julgado' } });

    const saveButton = screen.getByRole('button', { name: /Salvar Correção/i });
    expect(saveButton).not.toBeDisabled();
  });

  it('salva correção com sucesso', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 1,
        process_number: '0123456-78.2020.8.19.0001',
        original_phase: '02',
        corrected_phase: '03',
        reason: 'Encontrado trânsito em julgado',
        corrected_at: new Date().toISOString(),
      }),
    });

    render(
      <PhaseEditModal
        isOpen={true}
        processNumber="0123456-78.2020.8.19.0001"
        currentPhase="02"
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    const phaseSelect = screen.getByDisplayValue('02 - Conhecimento — Sentença sem Trânsito em Julgado');
    fireEvent.change(phaseSelect, { target: { value: '03' } });

    const textarea = screen.getByPlaceholderText(/Ex: Processo foi remetido/);
    fireEvent.change(textarea, { target: { value: 'Encontrado trânsito em julgado' } });

    const saveButton = screen.getByRole('button', { name: /Salvar Correção/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/processes/0123456-78.2020.8.19.0001/phase',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: expect.stringContaining('"corrected_phase":"03"'),
        })
      );
      expect(toastModule.toast.success).toHaveBeenCalledWith(
        'Fase corrigida com sucesso!'
      );
      expect(mockOnSave).toHaveBeenCalled();
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  it('exibe erro quando fetch falha', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      statusText: 'Internal Server Error',
    });

    render(
      <PhaseEditModal
        isOpen={true}
        processNumber="0123456-78.2020.8.19.0001"
        currentPhase="02"
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    const textarea = screen.getByPlaceholderText(/Ex: Processo foi remetido/);
    fireEvent.change(textarea, { target: { value: 'Encontrado trânsito em julgado' } });

    const saveButton = screen.getByRole('button', { name: /Salvar Correção/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(toastModule.toast.error).toHaveBeenCalledWith(
        expect.stringContaining('Erro')
      );
      expect(mockOnSave).not.toHaveBeenCalled();
    });
  });

  it('reseta estado ao fechar modal', async () => {
    render(
      <PhaseEditModal
        isOpen={true}
        processNumber="0123456-78.2020.8.19.0001"
        currentPhase="02"
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    const textarea = screen.getByPlaceholderText(/Ex: Processo foi remetido/);
    fireEvent.change(textarea, { target: { value: 'Texto de motivo' } });

    const closeButton = screen.getByRole('button', { name: /Fechar/i });
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('exibe caracteres restantes corretamente', () => {
    render(
      <PhaseEditModal
        isOpen={true}
        processNumber="0123456-78.2020.8.19.0001"
        currentPhase="02"
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    const textarea = screen.getByPlaceholderText(/Ex: Processo foi remetido/);
    expect(screen.getByText('0/500 caracteres')).toBeInTheDocument();

    fireEvent.change(textarea, { target: { value: 'Test motivo' } });
    expect(screen.getByText('11/500 caracteres')).toBeInTheDocument();
  });

  it('permite selecionar diferentes fases', () => {
    render(
      <PhaseEditModal
        isOpen={true}
        processNumber="0123456-78.2020.8.19.0001"
        currentPhase="02"
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    const phaseSelect = screen.getByDisplayValue('02 - Conhecimento — Sentença sem Trânsito em Julgado');
    fireEvent.change(phaseSelect, { target: { value: '05' } });

    expect(phaseSelect).toHaveValue('05');
  });

  it('mostra estado de salvamento durante requisição', async () => {
    let resolveResponse;
    global.fetch.mockImplementationOnce(
      () => new Promise((resolve) => {
        resolveResponse = () => resolve({
          ok: true,
          json: async () => ({ id: 1 }),
        });
      })
    );

    render(
      <PhaseEditModal
        isOpen={true}
        processNumber="0123456-78.2020.8.19.0001"
        currentPhase="02"
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    const textarea = screen.getByPlaceholderText(/Ex: Processo foi remetido/);
    fireEvent.change(textarea, { target: { value: 'Motivo qualquer' } });

    const saveButton = screen.getByRole('button', { name: /Salvar Correção/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Salvando/i })).toBeInTheDocument();
    });

    resolveResponse();

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Salvar Correção/i })).toBeInTheDocument();
    });
  });

  it('limita texto ao máximo de 500 caracteres (atributo HTML)', () => {
    render(
      <PhaseEditModal
        isOpen={true}
        processNumber="0123456-78.2020.8.19.0001"
        currentPhase="02"
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    const textarea = screen.getByPlaceholderText(/Ex: Processo foi remetido/);
    expect(textarea).toHaveAttribute('maxlength', '500');
  });
});

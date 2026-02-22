import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import ProcessDetails from '../components/ProcessDetails';

// Mock das dependências
vi.mock('../utils/phaseColors', () => ({
  getPhaseColorClasses: () => 'bg-blue-100 text-blue-800',
}));

vi.mock('../constants/phases', () => ({
  normalizePhaseWithMovements: (phase) => phase || '01',
}));

vi.mock('../services/api', () => ({
  getProcessInstance: vi.fn(),
  getProcessInstances: vi.fn().mockResolvedValue([]),
}));

vi.mock('react-hot-toast', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

const mockProcessData = {
  number: '00000001010000100001',
  tribunal_name: 'TJSP',
  class_nature: 'Ação de Cobrança',
  subject: 'Cobrança de Dívida',
  court: 'TJSP - 1ª Vara Cível',
  court_unit: '1ª Vara Cível',
  district: '3550308',
  phase: '01',
  distribution_date: '2024-01-15T10:00:00',
  last_update: '2024-01-16T14:30:00',
  movements: [
    {
      date: '2024-01-15T10:00:00',
      description: 'Distribuição',
      code: '11011',
    },
    {
      date: '2024-01-16T14:30:00',
      description: 'Petição Inicial',
      code: '85',
    },
  ],
};

describe('ProcessDetails Component', () => {
  it('renders process number', () => {
    const { container } = render(<ProcessDetails data={mockProcessData} />);

    expect(container.textContent).toContain('00000001010000100001');
  });

  it('renders tribunal name', () => {
    const { container } = render(<ProcessDetails data={mockProcessData} />);

    expect(container.textContent).toContain('TJSP');
  });

  it('renders class nature', () => {
    const { container } = render(<ProcessDetails data={mockProcessData} />);

    expect(container.textContent).toContain('Ação de Cobrança');
  });

  it('renders process phase', () => {
    render(<ProcessDetails data={mockProcessData} />);

    // Phase should be displayed somewhere
    const phaseElements = screen.queryAllByText(/fase/i);
    expect(phaseElements.length).toBeGreaterThan(0);
  });

  it('renders movements list', () => {
    render(<ProcessDetails data={mockProcessData} />);

    // Use queryAllByText for texts that may appear multiple times
    const distributionTexts = screen.queryAllByText(/Distribuição/);
    const petitionTexts = screen.queryAllByText(/Petição Inicial/);

    expect(distributionTexts.length).toBeGreaterThan(0);
    expect(petitionTexts.length).toBeGreaterThan(0);
  });

  it('handles empty movements gracefully', () => {
    const dataWithoutMovements = {
      ...mockProcessData,
      movements: [],
    };

    const { container } = render(<ProcessDetails data={dataWithoutMovements} />);
    expect(container).toBeTruthy();
  });

  it('renders court information', () => {
    const { container } = render(<ProcessDetails data={mockProcessData} />);

    expect(container.textContent).toContain('1ª Vara Cível');
  });
});

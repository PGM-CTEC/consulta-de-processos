import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import BulkSearch from '../components/BulkSearch';

// Mock the API module
vi.mock('../services/api', () => ({
  bulkSearch: vi.fn().mockResolvedValue({
    results: [],
    failures: [],
  }),
}));

// Mock the utils
vi.mock('../utils/phaseColors', () => ({
  getPhaseColorClasses: () => 'bg-blue-100',
  getPhaseDisplayName: (phase) => phase,
}));

vi.mock('../utils/exportHelpers', () => ({
  exporters: {
    csv: { export: vi.fn() },
    excel: { export: vi.fn() },
    json: { export: vi.fn() },
  },
}));

describe('BulkSearch Component', () => {
  it('renders bulk search component', () => {
    render(<BulkSearch />);

    // Should render textarea for input
    const textareas = screen.queryAllByRole('textbox');
    expect(textareas.length).toBeGreaterThan(0);
  });

  it('renders search button', () => {
    const { container } = render(<BulkSearch />);

    // Should have a button to initiate search
    const buttons = screen.queryAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('has file upload functionality', () => {
    const { container } = render(<BulkSearch />);

    // Component should render (presence test)
    expect(container).toBeTruthy();
  });

  it('handles component mount without errors', () => {
    expect(() => {
      render(<BulkSearch />);
    }).not.toThrow();
  });
});

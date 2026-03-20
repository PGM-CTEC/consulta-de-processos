import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SearchProcess from '../components/SearchProcess';

const mockLabels = {
  search: {
    placeholder: 'Digite o número do processo (CNJ)',
    button: 'Buscar',
    loading: 'Buscando...',
  },
};

describe('SearchProcess Component', () => {
  it('renders search input and button', () => {
    const mockOnSearch = vi.fn();
    render(<SearchProcess onSearch={mockOnSearch} loading={false} labels={mockLabels} />);

    const input = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /buscar/i });

    expect(input).toBeInTheDocument();
    expect(button).toBeInTheDocument();
  });

  it('calls onSearch when form is submitted with valid number', async () => {
    const mockOnSearch = vi.fn();
    const user = userEvent.setup();

    render(<SearchProcess onSearch={mockOnSearch} loading={false} labels={mockLabels} />);

    const input = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /buscar/i });

    await user.type(input, '00000001010000100001');
    await user.click(button);

    expect(mockOnSearch).toHaveBeenCalledWith('00000001010000100001');
    expect(mockOnSearch).toHaveBeenCalledTimes(1);
  });

  it('does not call onSearch when form is submitted with empty number', async () => {
    const mockOnSearch = vi.fn();
    const user = userEvent.setup();

    render(<SearchProcess onSearch={mockOnSearch} loading={false} labels={mockLabels} />);

    const button = screen.getByRole('button', { name: /buscar/i });

    await user.click(button);

    expect(mockOnSearch).not.toHaveBeenCalled();
  });

  it('disables input and button when loading', () => {
    const mockOnSearch = vi.fn();

    render(<SearchProcess onSearch={mockOnSearch} loading={true} labels={mockLabels} />);

    const input = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /buscando/i });

    expect(input).toBeDisabled();
    expect(button).toBeDisabled();
  });

  it('shows loading state when loading prop is true', () => {
    const mockOnSearch = vi.fn();

    render(<SearchProcess onSearch={mockOnSearch} loading={true} labels={mockLabels} />);

    expect(screen.getByText(/buscando/i)).toBeInTheDocument();
  });

  it('trims whitespace from input before calling onSearch', async () => {
    const mockOnSearch = vi.fn();
    const user = userEvent.setup();

    render(<SearchProcess onSearch={mockOnSearch} loading={false} labels={mockLabels} />);

    const input = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /buscar/i });

    await user.type(input, '  00000001010000100001  ');
    await user.click(button);

    expect(mockOnSearch).toHaveBeenCalledWith('00000001010000100001');
  });

  it('has accessible labels', () => {
    const mockOnSearch = vi.fn();

    render(<SearchProcess onSearch={mockOnSearch} loading={false} labels={mockLabels} />);

    const input = screen.getByLabelText(/digite o número do processo/i);
    expect(input).toBeInTheDocument();
  });
});

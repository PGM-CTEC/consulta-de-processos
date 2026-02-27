/**
 * Atomic Components Tests — REM-034
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';

describe('Button — REM-034', () => {
  it('renders with default variant', () => {
    render(<Button>Clique aqui</Button>);
    expect(screen.getByRole('button', { name: 'Clique aqui' })).toBeTruthy();
  });

  it('renders secondary variant', () => {
    render(<Button variant="secondary">Secundário</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('bg-secondary');
  });

  it('renders ghost variant', () => {
    render(<Button variant="ghost">Ghost</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('hover:bg-accent');
  });

  it('renders link variant', () => {
    render(<Button variant="link">Link</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('underline');
  });

  it('is accessible (is a native button)', () => {
    render(<Button>Acessível</Button>);
    expect(screen.getByRole('button').tagName).toBe('BUTTON');
  });

  it('supports disabled state', () => {
    render(<Button disabled>Desabilitado</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('renders small size', () => {
    render(<Button size="sm">Pequeno</Button>);
    expect(screen.getByRole('button').className).toContain('h-9');
  });

  it('renders large size', () => {
    render(<Button size="lg">Grande</Button>);
    expect(screen.getByRole('button').className).toContain('h-11');
  });
});

describe('Card — REM-034', () => {
  it('renders card with header and content', () => {
    render(
      <Card>
        <CardHeader><CardTitle>Título</CardTitle></CardHeader>
        <CardContent>Conteúdo</CardContent>
      </Card>
    );
    expect(screen.getByText('Título')).toBeTruthy();
    expect(screen.getByText('Conteúdo')).toBeTruthy();
  });

  it('CardTitle renders as h3', () => {
    render(<CardTitle>Meu Card</CardTitle>);
    expect(screen.getByRole('heading', { level: 3 })).toBeTruthy();
  });
});

describe('Badge — REM-034', () => {
  it('renders with text', () => {
    render(<Badge>Ativo</Badge>);
    expect(screen.getByText('Ativo')).toBeTruthy();
  });

  it('renders secondary variant', () => {
    const { container } = render(<Badge variant="secondary">Draft</Badge>);
    expect(container.firstChild.className).toContain('bg-secondary');
  });

  it('renders destructive variant', () => {
    const { container } = render(<Badge variant="destructive">Erro</Badge>);
    expect(container.firstChild.className).toContain('bg-destructive');
  });
});

describe('Input — REM-034', () => {
  it('renders text input', () => {
    render(<Input type="text" placeholder="Digite aqui" />);
    expect(screen.getByPlaceholderText('Digite aqui')).toBeTruthy();
  });

  it('is accessible (textbox role)', () => {
    render(<Input type="text" aria-label="Nome" />);
    expect(screen.getByRole('textbox')).toBeTruthy();
  });

  it('supports disabled state', () => {
    render(<Input disabled placeholder="Desabilitado" />);
    expect(screen.getByPlaceholderText('Desabilitado')).toBeDisabled();
  });
});

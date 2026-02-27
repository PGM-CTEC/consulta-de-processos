import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { LoadingState, SkeletonCard, SkeletonTable, ErrorState } from '../components/LoadingState'

describe('LoadingState', () => {
  it('renders spinner variant by default', () => {
    render(<LoadingState />)
    expect(document.querySelector('.animate-spin')).toBeTruthy()
  })

  it('renders spinner with custom message', () => {
    render(<LoadingState variant="spinner" message="Carregando processos..." />)
    expect(screen.getByText('Carregando processos...')).toBeTruthy()
  })

  it('renders skeleton variant', () => {
    render(<LoadingState variant="skeleton" />)
    expect(document.querySelector('.animate-pulse')).toBeTruthy()
  })

  it('renders text variant with default message', () => {
    render(<LoadingState variant="text" />)
    expect(screen.getByText('Carregando...')).toBeTruthy()
  })

  it('renders text variant with custom message', () => {
    render(<LoadingState variant="text" message="Aguarde..." />)
    expect(screen.getByText('Aguarde...')).toBeTruthy()
  })
})

describe('SkeletonCard', () => {
  it('renders animated placeholder bars', () => {
    render(<SkeletonCard />)
    expect(document.querySelector('.animate-pulse')).toBeTruthy()
  })
})

describe('SkeletonTable', () => {
  it('renders correct number of skeleton rows', () => {
    render(<SkeletonTable rows={3} />)
    const rows = document.querySelectorAll('.animate-pulse')
    expect(rows.length).toBeGreaterThanOrEqual(3)
  })

  it('renders default 5 rows when no rows prop', () => {
    render(<SkeletonTable />)
    const rows = document.querySelectorAll('.animate-pulse')
    expect(rows.length).toBeGreaterThanOrEqual(5)
  })
})

describe('ErrorState', () => {
  it('renders error message', () => {
    render(<ErrorState message="Erro ao carregar dados" />)
    expect(screen.getByText('Erro ao carregar dados')).toBeTruthy()
  })

  it('renders retry button when onRetry provided', () => {
    const onRetry = () => {}
    render(<ErrorState message="Erro" onRetry={onRetry} />)
    expect(screen.getByRole('button', { name: /tentar novamente/i })).toBeTruthy()
  })

  it('does not render retry button when no onRetry', () => {
    render(<ErrorState message="Erro" />)
    const btn = screen.queryByRole('button')
    expect(btn).toBeNull()
  })
})

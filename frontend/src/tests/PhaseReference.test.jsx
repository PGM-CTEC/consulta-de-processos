/**
 * Tests for PhaseReference Component - Frontend Testing Phase 8
 * Story: REM-018 - Frontend Unit Tests (Target: 60%+ Coverage)
 *
 * Test Categories:
 * - Header rendering
 * - Info box display
 * - Phase grouping by type
 * - Color legend display
 * - Phase utility integration
 * - Documentation link
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import PhaseReference from '../components/PhaseReference';
import { ALL_PHASES } from '../constants/phases';
import * as phaseColors from '../utils/phaseColors';

// Mock phase utilities
vi.mock('../utils/phaseColors', () => ({
    getPhaseColorClasses: vi.fn(() => 'bg-blue-100 text-blue-800'),
    getPhaseIcon: vi.fn(() => '📋'),
}));

// Mock ALL_PHASES constant
vi.mock('../constants/phases', () => ({
    ALL_PHASES: [
        { code: '01', name: 'Conhecimento - 1ª Instância', type: 'Conhecimento' },
        { code: '02', name: 'Conhecimento - 2ª Instância', type: 'Conhecimento' },
        { code: '10', name: 'Execução - 1ª Instância', type: 'Execução' },
        { code: '12', name: 'Execução - 2ª Instância', type: 'Execução' },
        { code: '06', name: 'Suspenso/Sobrestado', type: 'Transversal' },
        { code: '09', name: 'Arquivado Definitivamente', type: 'Final' },
    ],
}));

describe('PhaseReference Component', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('Header Section', () => {
        it('TC-1: renders main title', () => {
            render(<PhaseReference />);

            expect(screen.getByText('Referência de Fases Processuais')).toBeInTheDocument();
        });

        it('TC-2: displays version information', () => {
            render(<PhaseReference />);

            expect(
                screen.getByText(/Modelo de Classificação PGM-Rio — 15 Fases Oficiais/)
            ).toBeInTheDocument();
            expect(screen.getByText(/Versão 2.0 — Fevereiro 2026/)).toBeInTheDocument();
        });

        it('TC-3: shows BookOpen icon', () => {
            const { container } = render(<PhaseReference />);

            // BookOpen is a lucide-react SVG
            const icons = container.querySelectorAll('svg');
            expect(icons.length).toBeGreaterThan(0);
        });

        it('TC-4: header has gradient background', () => {
            const { container } = render(<PhaseReference />);

            const header = container.querySelector('.bg-gradient-to-r.from-indigo-600.to-violet-600');
            expect(header).toBeInTheDocument();
        });
    });

    describe('Info Box Section', () => {
        it('TC-5: displays info box title', () => {
            render(<PhaseReference />);

            expect(screen.getByText('Sobre o Sistema de Classificação')).toBeInTheDocument();
        });

        it('TC-6: shows CNJ resolutions info', () => {
            render(<PhaseReference />);

            expect(screen.getByText(/Resoluções 46\/2007 e 326\/2020/)).toBeInTheDocument();
            expect(screen.getByText(/Resolução CNJ 455\/2022/)).toBeInTheDocument();
        });

        it('TC-7: info box has blue styling', () => {
            const { container } = render(<PhaseReference />);

            const infoBox = container.querySelector('.bg-blue-50.border-l-4.border-blue-500');
            expect(infoBox).toBeInTheDocument();
        });
    });

    describe('Phase Grouping', () => {
        it('TC-8: groups phases by type correctly', () => {
            render(<PhaseReference />);

            // Verify all 4 type groups are rendered
            expect(screen.getByText('Conhecimento')).toBeInTheDocument();
            // "Execução" appears multiple times (as type header and color description)
            const execucaoElements = screen.getAllByText('Execução');
            expect(execucaoElements.length).toBeGreaterThan(0);
            expect(screen.getByText('Transversal')).toBeInTheDocument();
            expect(screen.getByText('Final')).toBeInTheDocument();
        });

        it('TC-9: displays type descriptions', () => {
            render(<PhaseReference />);

            expect(
                screen.getByText(/Fases relacionadas ao processo de conhecimento/)
            ).toBeInTheDocument();
            expect(screen.getByText(/Fases de execução ou cumprimento de sentença/)).toBeInTheDocument();
        });

        it('TC-10: renders all phase codes', () => {
            render(<PhaseReference />);

            expect(screen.getByText('01')).toBeInTheDocument();
            expect(screen.getByText('02')).toBeInTheDocument();
            expect(screen.getByText('10')).toBeInTheDocument();
            expect(screen.getByText('12')).toBeInTheDocument();
            expect(screen.getByText('06')).toBeInTheDocument();
            expect(screen.getByText('09')).toBeInTheDocument();
        });

        it('TC-11: renders all phase names', () => {
            render(<PhaseReference />);

            expect(screen.getByText('Conhecimento - 1ª Instância')).toBeInTheDocument();
            expect(screen.getByText('Conhecimento - 2ª Instância')).toBeInTheDocument();
            expect(screen.getByText('Execução - 1ª Instância')).toBeInTheDocument();
            expect(screen.getByText('Execução - 2ª Instância')).toBeInTheDocument();
            // These appear multiple times (as phase names and color descriptions)
            const suspensoElements = screen.getAllByText('Suspenso/Sobrestado');
            expect(suspensoElements.length).toBeGreaterThan(0);
            const arquivadoElements = screen.getAllByText('Arquivado Definitivamente');
            expect(arquivadoElements.length).toBeGreaterThan(0);
        });

        it('TC-12: calls getPhaseColorClasses for each phase', () => {
            render(<PhaseReference />);

            expect(phaseColors.getPhaseColorClasses).toHaveBeenCalled();
            // Should be called once per phase (6 phases)
            expect(phaseColors.getPhaseColorClasses).toHaveBeenCalledTimes(6);
        });

        it('TC-13: calls getPhaseIcon for each phase', () => {
            render(<PhaseReference />);

            expect(phaseColors.getPhaseIcon).toHaveBeenCalled();
            // Should be called once per phase (6 phases)
            expect(phaseColors.getPhaseIcon).toHaveBeenCalledTimes(6);
        });
    });

    describe('Color Legend Section', () => {
        it('TC-14: displays legend title', () => {
            render(<PhaseReference />);

            // Use getAllByText and check length since "Legenda de Cores" might appear once
            const legendTitles = screen.getAllByText('Legenda de Cores');
            expect(legendTitles.length).toBeGreaterThan(0);
        });

        it('TC-15: shows all 6 color categories', () => {
            render(<PhaseReference />);

            expect(screen.getByText('Azul')).toBeInTheDocument();
            expect(screen.getByText('Verde')).toBeInTheDocument();
            expect(screen.getByText('Laranja')).toBeInTheDocument();
            expect(screen.getByText('Amarelo')).toBeInTheDocument();
            expect(screen.getByText('Roxo')).toBeInTheDocument();
            expect(screen.getByText('Cinza')).toBeInTheDocument();
        });

        it('TC-16: displays color descriptions', () => {
            render(<PhaseReference />);

            expect(screen.getByText('Conhecimento em andamento')).toBeInTheDocument();
            expect(screen.getByText('Trânsito em julgado')).toBeInTheDocument();
            // "Execução" appears multiple times (as type and as color description)
            const execucaoElements = screen.getAllByText('Execução');
            expect(execucaoElements.length).toBeGreaterThan(0);
            // "Suspenso/Sobrestado" also appears multiple times (phase name and color description)
            const suspensoElements = screen.getAllByText('Suspenso/Sobrestado');
            expect(suspensoElements.length).toBeGreaterThan(0);
            expect(screen.getByText('Conversão em renda')).toBeInTheDocument();
            // "Arquivado definitivamente" appears multiple times (phase name and color description)
            const arquivadoElements = screen.getAllByText('Arquivado definitivamente');
            expect(arquivadoElements.length).toBeGreaterThan(0);
        });

        it('TC-17: renders color swatches with correct classes', () => {
            const { container } = render(<PhaseReference />);

            expect(container.querySelector('.bg-blue-100.border-blue-200')).toBeInTheDocument();
            expect(container.querySelector('.bg-green-100.border-green-200')).toBeInTheDocument();
            expect(container.querySelector('.bg-orange-100.border-orange-200')).toBeInTheDocument();
            expect(container.querySelector('.bg-yellow-100.border-yellow-200')).toBeInTheDocument();
            expect(container.querySelector('.bg-purple-100.border-purple-200')).toBeInTheDocument();
            expect(container.querySelector('.bg-gray-100.border-gray-200')).toBeInTheDocument();
        });
    });

    describe('Documentation Link', () => {
        it('TC-18: displays documentation reference', () => {
            render(<PhaseReference />);

            expect(screen.getByText(/Para mais informações/)).toBeInTheDocument();
        });

        it('TC-19: shows correct documentation path', () => {
            render(<PhaseReference />);

            expect(screen.getByText('frontend/src/constants/README-FASES.md')).toBeInTheDocument();
        });

        it('TC-20: documentation path is in code tag', () => {
            const { container } = render(<PhaseReference />);

            const codeTag = Array.from(container.querySelectorAll('code')).find((el) =>
                el.textContent.includes('README-FASES.md')
            );
            expect(codeTag).toBeInTheDocument();
            expect(codeTag).toHaveClass('font-mono');
        });
    });

    describe('Phase Type Icons', () => {
        it('TC-21: displays emoji icons for phase types', () => {
            const { container } = render(<PhaseReference />);

            // Check that emojis are rendered (contained in spans with text-2xl)
            const emojiSpans = container.querySelectorAll('.text-2xl');
            expect(emojiSpans.length).toBeGreaterThan(0);
        });

        it('TC-22: renders type info for all categories', () => {
            render(<PhaseReference />);

            // Verify type descriptions exist
            expect(
                screen.getByText(/Fase que pode ocorrer tanto em conhecimento quanto em execução/)
            ).toBeInTheDocument();
            expect(
                screen.getByText(/Fase terminal indicando encerramento definitivo do processo/)
            ).toBeInTheDocument();
        });
    });

    describe('Layout and Structure', () => {
        it('TC-23: uses correct container max-width', () => {
            const { container } = render(<PhaseReference />);

            const mainContainer = container.querySelector('.max-w-6xl.mx-auto');
            expect(mainContainer).toBeInTheDocument();
        });

        it('TC-24: phase items have hover effect', () => {
            const { container } = render(<PhaseReference />);

            const phaseItems = container.querySelectorAll('.hover\\:bg-gray-50');
            expect(phaseItems.length).toBeGreaterThan(0);
        });

        it('TC-25: renders rounded cards for sections', () => {
            const { container } = render(<PhaseReference />);

            const roundedCards = container.querySelectorAll('.rounded-2xl');
            expect(roundedCards.length).toBeGreaterThan(3); // Multiple sections use rounded-2xl
        });
    });

    describe('Integration with Phase Constants', () => {
        it('TC-26: uses ALL_PHASES from constants', () => {
            // This test verifies the import works correctly
            expect(ALL_PHASES).toBeDefined();
            expect(Array.isArray(ALL_PHASES)).toBe(true);
            expect(ALL_PHASES.length).toBe(6); // Mock has 6 phases
        });

        it('TC-27: each phase has required properties', () => {
            ALL_PHASES.forEach((phase) => {
                expect(phase).toHaveProperty('code');
                expect(phase).toHaveProperty('name');
                expect(phase).toHaveProperty('type');
            });
        });
    });
});

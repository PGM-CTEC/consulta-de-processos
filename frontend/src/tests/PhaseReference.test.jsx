/**
 * Tests for PhaseReference Component
 *
 * PhaseReference.jsx foi reescrito para o modelo hierárquico (Estágio /
 * Subfase / Trânsito em Julgado). Esta suíte testa o componente atual,
 * usando as constantes reais de `constants/phases.js` (sem mock) para
 * que a suíte acompanhe automaticamente futuras mudanças em STAGES/SUBSTAGES.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import PhaseReference from '../components/PhaseReference';
import { STAGES, TRANSIT_OPTIONS, getSubstagesForStage } from '../constants/phases';

describe('PhaseReference Component', () => {
    describe('Header Section', () => {
        it('TC-1: renders main title', () => {
            render(<PhaseReference />);
            expect(screen.getByText('Referência de Classificação Processual')).toBeInTheDocument();
        });

        it('TC-2: displays hierarchical model subtitle', () => {
            render(<PhaseReference />);
            expect(
                screen.getByText('Modelo Hierárquico PGM-Rio — Estágio / Subfase / Trânsito em Julgado')
            ).toBeInTheDocument();
        });

        it('TC-3: shows BookOpen icon', () => {
            const { container } = render(<PhaseReference />);
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

    describe('Hierarchical Classification Section', () => {
        it('TC-8: renders section title', () => {
            render(<PhaseReference />);
            expect(screen.getByText('Classificação Hierárquica (3 Campos)')).toBeInTheDocument();
        });

        it('TC-9: renders all 5 stage labels', () => {
            render(<PhaseReference />);
            Object.values(STAGES).forEach((stage) => {
                expect(screen.getByText(`${stage.value}. ${stage.label}`)).toBeInTheDocument();
            });
        });

        it('TC-10: renders substages nested under stage 1', () => {
            render(<PhaseReference />);
            const stage1Substages = getSubstagesForStage(1);
            expect(stage1Substages.length).toBeGreaterThan(0);
            stage1Substages.forEach((ss) => {
                expect(screen.getByText(ss.label)).toBeInTheDocument();
            });
        });

        it('TC-11: renders substages nested under stage 2', () => {
            render(<PhaseReference />);
            const stage2Substages = getSubstagesForStage(2);
            expect(stage2Substages.length).toBeGreaterThan(0);
            stage2Substages.forEach((ss) => {
                expect(screen.getByText(ss.label)).toBeInTheDocument();
            });
        });

        it('TC-12: stages 3, 4 and 5 have no substages', () => {
            [3, 4, 5].forEach((stageValue) => {
                expect(getSubstagesForStage(stageValue)).toHaveLength(0);
            });
        });

        it('TC-13: renders stage badge with getStageColorClasses styling', () => {
            render(<PhaseReference />);
            // STAGES[1].color === 'blue' -> getStageColorClasses(1) inclui 'bg-blue-100 text-blue-800'
            const stage1Badge = screen.getByText('1. Conhecimento');
            expect(stage1Badge.className).toContain('bg-blue-100');
            expect(stage1Badge.className).toContain('text-blue-800');
        });
    });

    describe('Trânsito em Julgado Section', () => {
        it('TC-14: renders section title', () => {
            render(<PhaseReference />);
            expect(screen.getByText('Trânsito em Julgado (campo independente)')).toBeInTheDocument();
        });

        it('TC-15: renders all transit options', () => {
            render(<PhaseReference />);
            Object.values(TRANSIT_OPTIONS).forEach((t) => {
                expect(screen.getByText(`${t.value} = ${t.label}`)).toBeInTheDocument();
            });
        });
    });

    describe('Documentation Link', () => {
        it('TC-16: displays documentation reference', () => {
            render(<PhaseReference />);
            expect(screen.getByText(/Para mais informações/)).toBeInTheDocument();
        });

        it('TC-17: shows correct documentation path', () => {
            render(<PhaseReference />);
            expect(screen.getByText('frontend/src/constants/README-FASES.md')).toBeInTheDocument();
        });

        it('TC-18: documentation path is in code tag', () => {
            const { container } = render(<PhaseReference />);
            const codeTag = Array.from(container.querySelectorAll('code')).find((el) =>
                el.textContent.includes('README-FASES.md')
            );
            expect(codeTag).toBeInTheDocument();
            expect(codeTag).toHaveClass('font-mono');
        });
    });

    describe('Layout and Structure', () => {
        it('TC-19: uses correct container max-width', () => {
            const { container } = render(<PhaseReference />);
            const mainContainer = container.querySelector('.max-w-6xl.mx-auto');
            expect(mainContainer).toBeInTheDocument();
        });

        it('TC-20: renders rounded cards for sections', () => {
            const { container } = render(<PhaseReference />);
            const roundedCards = container.querySelectorAll('.rounded-2xl');
            expect(roundedCards.length).toBeGreaterThanOrEqual(2);
        });
    });
});

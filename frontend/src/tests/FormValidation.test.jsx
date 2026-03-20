/**
 * Tests for Form Validation — REM-040
 *
 * Covers:
 * - validationSchemas.js (cnjNumberSchema, bulkSearchSchema, sqlConfigSchema)
 * - BulkSearch validation behavior (inline errors, submit prevention)
 * - SearchProcess validation behavior
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// ─── Schema unit tests ─────────────────────────────────────────────────────

import {
    cnjNumberSchema,
    bulkSearchSchema,
    sqlConfigSchema,
} from '../lib/validationSchemas';

/** Synchronously validates a Zod v4 Standard-Schema schema */
function validate(schema, value) {
    const result = schema['~standard'].validate(value);
    return result;
}

describe('validationSchemas', () => {
    describe('cnjNumberSchema', () => {
        it('accepts formatted CNJ number', () => {
            const r = validate(cnjNumberSchema, '0001745-64.1989.8.19.0002');
            expect(r.issues).toBeUndefined();
        });

        it('accepts raw 20-digit CNJ number', () => {
            const r = validate(cnjNumberSchema, '00017456419898190002');
            expect(r.issues).toBeUndefined();
        });

        it('rejects empty string', () => {
            const r = validate(cnjNumberSchema, '');
            expect(r.issues).toBeDefined();
            expect(r.issues[0].message).toMatch(/obrigatório/i);
        });

        it('rejects invalid format', () => {
            const r = validate(cnjNumberSchema, '12345-invalid');
            expect(r.issues).toBeDefined();
            expect(r.issues[0].message).toMatch(/CNJ inválido/i);
        });

        it('rejects number with wrong digit count', () => {
            const r = validate(cnjNumberSchema, '1234567');
            expect(r.issues).toBeDefined();
        });
    });

    describe('bulkSearchSchema', () => {
        it('accepts a single valid number', () => {
            const r = validate(bulkSearchSchema, { numbers: '0001745-64.1989.8.19.0002' });
            expect(r.issues).toBeUndefined();
        });

        it('accepts multiple numbers separated by newlines', () => {
            const r = validate(bulkSearchSchema, {
                numbers: '0001745-64.1989.8.19.0002\n0002345-12.2020.8.19.0001',
            });
            expect(r.issues).toBeUndefined();
        });

        it('rejects empty string', () => {
            const r = validate(bulkSearchSchema, { numbers: '' });
            expect(r.issues).toBeDefined();
        });
    });

    describe('sqlConfigSchema', () => {
        const validConfig = {
            driver: 'postgresql',
            host: 'localhost',
            port: 5432,
            user: 'admin',
            password: 'secret',
            database: 'mydb',
            query: 'SELECT * FROM t',
        };

        it('accepts valid SQL config', () => {
            const r = validate(sqlConfigSchema, validConfig);
            expect(r.issues).toBeUndefined();
        });

        it('rejects missing host', () => {
            const r = validate(sqlConfigSchema, { ...validConfig, host: '' });
            expect(r.issues).toBeDefined();
        });

        it('rejects port out of range', () => {
            const r = validate(sqlConfigSchema, { ...validConfig, port: 99999 });
            expect(r.issues).toBeDefined();
        });

        it('rejects missing database', () => {
            const r = validate(sqlConfigSchema, { ...validConfig, database: '' });
            expect(r.issues).toBeDefined();
        });

        it('accepts optional user and password', () => {
            const r = validate(sqlConfigSchema, { ...validConfig, user: undefined, password: undefined });
            expect(r.issues).toBeUndefined();
        });
    });
});

// ─── BulkSearch form behavior ─────────────────────────────────────────────

import BulkSearch from '../components/BulkSearch';
import * as api from '../services/api';
vi.mock('../services/api');
vi.mock('../utils/phaseColors', () => ({
    getPhaseColorClasses: vi.fn(() => 'bg-blue-100 text-blue-800'),
    getPhaseDisplayName: vi.fn((phase) => `Fase ${phase}`),
}));
vi.mock('../utils/exportHelpers', () => ({
    exporters: { csv: vi.fn(), xlsx: vi.fn(), txt: vi.fn(), md: vi.fn() },
}));

// eslint-disable-next-line no-undef
global.FileReader = class {
    readAsText(file) { this.onload({ target: { result: file.content } }); }
    readAsBinaryString(file) { this.onload({ target: { result: file.content } }); }
};

describe('BulkSearch — form validation', () => {
    beforeEach(() => { vi.clearAllMocks(); });

    it('submit button is disabled when textarea is empty', () => {
        render(<BulkSearch />);
        const btn = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
        expect(btn).toBeDisabled();
    });

    it('submit button enables when numbers are typed', async () => {
        const user = userEvent.setup();
        render(<BulkSearch />);
        const textarea = screen.getByPlaceholderText(/Um número por linha/i);
        await user.type(textarea, '0001745-64.1989.8.19.0002');
        const btn = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
        expect(btn).toBeEnabled();
    });

    it('submit button remains disabled with only whitespace', async () => {
        const user = userEvent.setup();
        render(<BulkSearch />);
        const textarea = screen.getByPlaceholderText(/Um número por linha/i);
        await user.type(textarea, '   ');
        const btn = screen.getByRole('button', { name: /Iniciar Consulta em Lote/i });
        expect(btn).toBeDisabled();
    });

    it('calls bulkSearch on valid submit', async () => {
        const user = userEvent.setup();
        api.bulkSubmit.mockResolvedValue({ job_id: 'test-job-123' });
        api.getBulkJob.mockResolvedValue({ status: 'done', results: [], failures: [] });
        render(<BulkSearch />);
        const textarea = screen.getByPlaceholderText(/Um número por linha/i);
        await user.type(textarea, '0001745-64.1989.8.19.0002');
        await user.click(screen.getByRole('button', { name: /Iniciar Consulta em Lote/i }));
        await waitFor(() => expect(api.bulkSubmit).toHaveBeenCalledWith(['0001745-64.1989.8.19.0002']));
    });

    it('shows API error inline on search failure', async () => {
        const user = userEvent.setup();
        api.bulkSubmit.mockRejectedValue(new Error('fail'));
        render(<BulkSearch />);
        await user.type(screen.getByPlaceholderText(/Um número por linha/i), '0001745-64.1989.8.19.0002');
        await user.click(screen.getByRole('button', { name: /Iniciar Consulta em Lote/i }));
        await waitFor(() => expect(screen.getByText(/Falha ao iniciar a busca em lote/i)).toBeInTheDocument());
    });

    it('preserves textarea value after API error', async () => {
        const user = userEvent.setup();
        api.bulkSubmit.mockRejectedValue(new Error('fail'));
        render(<BulkSearch />);
        const textarea = screen.getByPlaceholderText(/Um número por linha/i);
        const testNum = '0001745-64.1989.8.19.0002';
        await user.type(textarea, testNum);
        await user.click(screen.getByRole('button', { name: /Iniciar Consulta em Lote/i }));
        await waitFor(() => screen.getByText(/Falha ao iniciar/i));
        expect(textarea).toHaveValue(testNum);
    });
});

// ─── SearchProcess form behavior ──────────────────────────────────────────

import SearchProcess from '../components/SearchProcess';

const defaultLabels = {
    search: {
        placeholder: 'Número do processo',
        button: 'Buscar',
        loading: 'Carregando...',
    },
};

describe('SearchProcess — form validation', () => {
    it('renders the search input', () => {
        render(<SearchProcess onSearch={vi.fn()} loading={false} labels={defaultLabels} />);
        expect(screen.getByLabelText(/Número do processo/i)).toBeInTheDocument();
    });

    it('calls onSearch when a valid CNJ is submitted', async () => {
        const user = userEvent.setup();
        const onSearch = vi.fn();
        render(<SearchProcess onSearch={onSearch} loading={false} labels={defaultLabels} />);
        await user.type(screen.getByLabelText(/Número do processo/i), '0001745-64.1989.8.19.0002');
        await user.click(screen.getByRole('button', { name: /Buscar/i }));
        await waitFor(() => expect(onSearch).toHaveBeenCalledWith('0001745-64.1989.8.19.0002'));
    });

    it('shows validation error for empty submit', async () => {
        const user = userEvent.setup();
        const onSearch = vi.fn();
        render(<SearchProcess onSearch={onSearch} loading={false} labels={defaultLabels} />);
        await user.click(screen.getByRole('button', { name: /Buscar/i }));
        await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
        expect(onSearch).not.toHaveBeenCalled();
    });

    it('shows validation error for invalid CNJ format', async () => {
        const user = userEvent.setup();
        const onSearch = vi.fn();
        render(<SearchProcess onSearch={onSearch} loading={false} labels={defaultLabels} />);
        await user.type(screen.getByLabelText(/Número do processo/i), 'abc-invalid');
        await user.click(screen.getByRole('button', { name: /Buscar/i }));
        await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
        expect(onSearch).not.toHaveBeenCalled();
    });

    it('does not call onSearch when loading', () => {
        const onSearch = vi.fn();
        render(<SearchProcess onSearch={onSearch} loading={true} labels={defaultLabels} />);
        const btn = screen.getByRole('button');
        expect(btn).toBeDisabled();
    });
});

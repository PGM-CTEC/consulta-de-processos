import { z } from 'zod';

// CNJ number: formatted NNNNNNN-DD.AAAA.J.TT.OOOO or raw 20 digits
const CNJ_FORMATTED = /^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$/;
const CNJ_RAW = /^\d{20}$/;

export const cnjNumberSchema = z
    .string()
    .trim()
    .min(1, 'Número do processo é obrigatório')
    .refine(
        (val) => CNJ_FORMATTED.test(val) || CNJ_RAW.test(val),
        'Número CNJ inválido. Use o formato: NNNNNNN-DD.AAAA.J.TT.OOOO'
    );

export const searchProcessSchema = z.object({
    number: cnjNumberSchema,
});

export const bulkSearchSchema = z.object({
    numbers: z
        .string()
        .min(1, 'Insira pelo menos um número de processo')
        .refine(
            (val) => val.split('\n').map((n) => n.trim()).filter((n) => n.length > 0).length > 0,
            'Insira pelo menos um número de processo'
        ),
});

export const sqlConfigSchema = z.object({
    driver: z.enum(['postgresql', 'mysql', 'mssql+pyodbc', 'sqlite']),
    host: z.string().min(1, 'Host é obrigatório'),
    port: z.coerce
        .number({ error: 'Porta deve ser um número' })
        .int('Porta deve ser um número inteiro')
        .min(1, 'Porta inválida')
        .max(65535, 'Porta inválida'),
    user: z.string().optional(),
    password: z.string().optional(),
    database: z.string().min(1, 'Banco de dados é obrigatório'),
    query: z.string().min(1, 'Query SQL é obrigatória'),
});

import { useState, useEffect } from 'react';

const DEFAULT_LABELS = {
    app: {
        title: "Consulta Processual",
        subtitle: "DataJud Intelligence",
        statusOnline: "Status: Online",
        statusOffline: "Status: Offline",
        footerText: "© 2026 Consulta Processual. Dados providos por DataJud/CNJ."
    },
    nav: {
        single: "Consulta Individual",
        bulk: "Busca em Lote",
        analytics: "Analytics / BI",
        settings: "Configurações",
        history: "Histórico"
    },
    home: {
        heroTitle: "Consulte processos em",
        heroHighlight: "tempo real",
        heroSubtitle: "Acesse dados unificados do Poder Judiciário (DataJud) de forma simples e rápida."
    },
    search: {
        placeholder: "Nº do processo (ex: 0000000-00.2024.8.19.0001)",
        button: "Consultar Processo",
        loading: "Buscando...",
        success: "Processo encontrado!",
        error: "Erro ao buscar processo. Verifique o número ou tente novamente."
    }
};

export function useLabels() {
    const [labels, setLabels] = useState(DEFAULT_LABELS);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadLabels() {
            try {
                const response = await fetch('/config/labels.json');
                if (response.ok) {
                    const data = await response.json();
                    setLabels(data);
                } else {
                    console.warn('Could not load labels.json, using defaults.');
                }
            } catch (error) {
                console.error('Error loading labels:', error);
            } finally {
                setLoading(false);
            }
        }

        loadLabels();
    }, []);

    return { labels, loading };
}

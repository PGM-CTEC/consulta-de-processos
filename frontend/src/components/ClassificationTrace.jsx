import { STAGES, SUBSTAGES, TRANSIT_OPTIONS } from '../constants/phases';

export const RULE_LABELS = {
    P1_arquivamento: 'Arquivamento/Baixa Definitiva detectada como último evento relevante. Indica encerramento do processo.',
    P2_transito_em_julgado: 'Certidão de Trânsito em Julgado identificada. O mérito foi julgado e a decisão tornou-se definitiva.',
    P3_sentenca_com_remessa_posterior: 'Sentença proferida seguida de remessa ao tribunal. Indica recurso à 2ª instância pendente de julgamento.',
    P3_sentenca_sem_transito: 'Sentença proferida sem trânsito em julgado. O prazo recursal pode estar em curso.',
    P4_remessa_sem_sentenca: 'Remessa/recurso ao tribunal sem sentença de 1ª instância no acervo. Processo tramitando em 2ª instância.',
    P5_suspensao: 'Suspensão ou sobrestamento ativo. Processo aguarda decisão de outro feito ou determinação judicial.',
    P6_fallback_antes_sentenca: 'Nenhuma âncora processual encontrada (sentença, recurso, arquivamento). Processo em fase inicial de conhecimento.',
    E1_arquivamento: 'Arquivamento em processo de execução. Indica satisfação do crédito ou extinção.',
    E2_suspensao: 'Execução suspensa. Pode haver embargos, acordo ou determinação judicial.',
    E3_fallback: 'Execução em andamento. Nenhuma âncora de suspensão ou arquivamento encontrada.',
    empty_list_fallback: 'Lista de movimentos/documentos vazia. Sem dados suficientes para classificação.',
    fusion_not_found: 'Processo não localizado no banco Fusion/PAV.',
    fusion_error: 'Erro na consulta ao Fusion/PAV.',
    fusion_unavailable: 'Serviço Fusion/PAV não configurado no ambiente.',
};

export const BRANCH_LABELS = {
    conhecimento: 'Conhecimento',
    execucao: 'Execução',
};

function ConfidenceBadge({ confidence }) {
    if (confidence == null) return null;
    const pct = Math.round(confidence * 100);
    let color = 'bg-green-100 text-green-700 border-green-200';
    if (pct < 70) color = 'bg-red-100 text-red-700 border-red-200';
    else if (pct < 85) color = 'bg-amber-100 text-amber-700 border-amber-200';
    return (
        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold border ${color}`}>
            {pct}%
        </span>
    );
}

export default function ClassificationTrace({ log, classification, compact = false }) {
    if (!log) return null;

    return (
        <div className={`${compact ? 'p-4' : 'px-6 pb-4'} bg-gray-50 border-t border-gray-100 animate-in fade-in duration-200`}>
            {/* Classificação hierárquica (3 campos) */}
            <div className="py-2 mb-2">
                <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs text-gray-400 font-semibold uppercase tracking-wide">Resultado da Classificação</span>
                    <ConfidenceBadge confidence={log.confidence} />
                </div>
                {classification?.stage ? (
                    <div className="grid grid-cols-3 gap-3">
                        <div className="bg-white rounded-lg border border-gray-200 p-2.5">
                            <span className="text-xs text-gray-400 font-semibold uppercase tracking-wide block">Estágio</span>
                            <p className="text-sm font-bold text-gray-800 mt-0.5">
                                {classification.stage_label || STAGES[classification.stage]?.label || '—'}
                            </p>
                        </div>
                        <div className="bg-white rounded-lg border border-gray-200 p-2.5">
                            <span className="text-xs text-gray-400 font-semibold uppercase tracking-wide block">Subfase</span>
                            <p className="text-sm font-bold text-gray-800 mt-0.5">
                                {classification.substage
                                    ? (classification.substage_label || SUBSTAGES[classification.substage]?.label || classification.substage)
                                    : '—'}
                            </p>
                        </div>
                        <div className="bg-white rounded-lg border border-gray-200 p-2.5">
                            <span className="text-xs text-gray-400 font-semibold uppercase tracking-wide block">Trâns. Julg.</span>
                            <p className="text-sm font-bold text-gray-800 mt-0.5">
                                {classification.transit_julgado
                                    ? (TRANSIT_OPTIONS[classification.transit_julgado]?.label || classification.transit_julgado)
                                    : '—'}
                            </p>
                        </div>
                    </div>
                ) : (
                    <p className="text-sm text-gray-500 italic">Indefinido</p>
                )}
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 py-2 text-xs">
                <div>
                    <span className="text-gray-400 font-semibold uppercase tracking-wide block">Ramo</span>
                    <p className="text-gray-700 font-medium mt-0.5">
                        {BRANCH_LABELS[log.branch] || log.branch || 'N/A'}
                    </p>
                </div>
                <div>
                    <span className="text-gray-400 font-semibold uppercase tracking-wide block">Movimentos analisados</span>
                    <p className="text-gray-700 mt-0.5">{log.total_movimentos ?? 0}</p>
                </div>
                <div>
                    <span className="text-gray-400 font-semibold uppercase tracking-wide block">Classe normalizada</span>
                    <p className="text-gray-700 mt-0.5 truncate" title={log.classe_normalizada || ''}>
                        {log.classe_normalizada || 'N/A'}
                    </p>
                </div>
            </div>

            {/* Fundamento da regra — exibição expandida */}
            <div className="py-2 border-t border-gray-200 text-xs">
                <span className="text-gray-400 font-semibold uppercase tracking-wide block">Fundamento da regra aplicada</span>
                <p className="text-gray-800 mt-1 leading-relaxed">
                    {RULE_LABELS[log.rule_applied] || log.rule_applied || 'N/A'}
                </p>
            </div>

            {log.decisive_movement && (
                <div className="py-2 border-t border-gray-200 text-xs">
                    <span className="text-gray-400 font-semibold uppercase tracking-wide block">Movimento/documento decisivo</span>
                    <p className="text-gray-800 font-semibold mt-0.5">
                        {log.decisive_movement}
                        {log.decisive_movement_date && (
                            <span className="text-gray-500 font-normal ml-2">
                                ({new Date(log.decisive_movement_date).toLocaleDateString('pt-BR')})
                            </span>
                        )}
                    </p>
                </div>
            )}

            {log.anchor_matches && Object.keys(log.anchor_matches).length > 0 && (
                <div className="py-2 border-t border-gray-200 text-xs">
                    <span className="text-gray-400 font-semibold uppercase tracking-wide block mb-1">
                        Âncoras detectadas
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                        {Object.entries(log.anchor_matches).map(([key, idx]) => (
                            <span
                                key={key}
                                className={`px-2 py-0.5 rounded text-xs font-mono ${
                                    idx !== null
                                        ? 'bg-green-50 text-green-700 border border-green-200'
                                        : 'bg-gray-100 text-gray-400 border border-gray-200'
                                }`}
                            >
                                {key}: {idx !== null ? `#${idx}` : '—'}
                            </span>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

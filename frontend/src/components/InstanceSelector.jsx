import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Layers, MapPin, Calendar, AlertTriangle } from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { getProcessInstances } from '../services/api';

const EMPTY_INSTANCES = {
  instances: [],
  instances_count: 0,
  selected_index: 0,
  missing_expected_instances: [],
  source_limited: false,
  diagnostic_note: '',
};

const GRAU_LABELS = {
  G1:  '1ª Instância',
  JE:  '1ª Instância (Juizado Especial)',
  G2:  '2ª Instância',
  TR:  '2ª Instância (Turma Recursal)',
  SUP: 'Tribunais Superiores',
};

// Ordem de exibição: 1ªs instâncias → 2ªs instâncias → superiores.
// JE e TR são as instâncias dos Juizados Especiais (equivalentes a G1/G2).
const SLOT_ORDER = ['G1', 'JE', 'G2', 'TR', 'SUP'];

const normalizePayload = (payload) => {
  const list = Array.isArray(payload?.instances) ? payload.instances : [];
  const normalizedInstances = list.map((instance, index) => ({
    ...instance,
    index: typeof instance?.index === 'number' ? instance.index : index,
  }));
  const payloadCount =
    typeof payload?.instances_count === 'number'
      ? payload.instances_count
      : normalizedInstances.length;
  const payloadSelected =
    typeof payload?.selected_index === 'number' ? payload.selected_index : 0;

  return {
    instances: normalizedInstances,
    instances_count: payloadCount,
    selected_index: payloadSelected,
    missing_expected_instances: Array.isArray(payload?.missing_expected_instances)
      ? payload.missing_expected_instances
      : [],
    source_limited: Boolean(payload?.source_limited),
    diagnostic_note: payload?.diagnostic_note || '',
  };
};

/**
 * Componente para selecionar entre múltiplas instâncias de um processo
 */
const InstanceSelector = ({ processNumber, onInstanceChange, meta }) => {
  const [fetchedInstances, setFetchedInstances] = useState(null);
  const [selectedIndex, setSelectedIndex] = useState(
    typeof meta?.selected_index === 'number' ? meta.selected_index : 0
  );

  const normalizedMeta = meta && typeof meta === 'object' ? normalizePayload(meta) : EMPTY_INSTANCES;
  const hasMetaData =
    normalizedMeta.instances.length > 0 ||
    normalizedMeta.instances_count > 0 ||
    normalizedMeta.missing_expected_instances.length > 0;

  useEffect(() => {
    const loadInstances = async () => {
      try {
        const data = await getProcessInstances(processNumber);
        setFetchedInstances(normalizePayload(data && typeof data === 'object' ? data : {}));
      } catch (error) {
        console.error('Error fetching instances:', error);
        setFetchedInstances(EMPTY_INSTANCES);
      }
    };

    if (hasMetaData) {
      return;
    }

    void loadInstances();
  }, [processNumber, hasMetaData]);

  const instances = hasMetaData ? normalizedMeta : fetchedInstances;
  const loading = !hasMetaData && fetchedInstances === null;

  const handleSelect = (instance) => {
    if (!instance || typeof instance.index !== 'number') return;
    setSelectedIndex(instance.index);
    if (onInstanceChange) {
      onInstanceChange(instance);
    }
  };

  if (loading) return null;
  const list = Array.isArray(instances?.instances) ? instances.instances : [];
  const count = typeof instances?.instances_count === 'number' ? instances.instances_count : list.length;
  if (!instances || list.length === 0) return null;

  if (count <= 1 || list.length === 1) {
    return (
      <div className="mb-3">
        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-gray-100 text-gray-600 border border-gray-200">
          Somente 1 instância encontrada
        </span>
      </div>
    );
  }

  const fallbackSelectedIndex =
    typeof instances?.selected_index === 'number' ? instances.selected_index : 0;
  const selectedInstance =
    list.find((instance) => instance.index === selectedIndex) ||
    list.find((instance) => instance.index === fallbackSelectedIndex) ||
    list[0];
  // Mostra apenas slots que têm instância (sem slots missing/vazios).
  const slots = SLOT_ORDER
    .map((grau) => ({
      grau,
      instance: list.find((item) => item.grau === grau),
    }))
    .filter((slot) => slot.instance);

  const gridCols = slots.length <= 2 ? 'md:grid-cols-2' : 'md:grid-cols-3';

  return (
    <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-xl p-4 mb-4 space-y-3">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center space-x-3 min-w-0">
          <div className="bg-purple-600 p-2 rounded-lg shrink-0">
            <Layers className="h-5 w-5 text-white" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-bold text-purple-900">Multiplas Instancias Disponiveis</p>
            <p className="text-xs text-purple-600">
              {instances.instances_count} instancias encontradas - Mostrando:{' '}
              {GRAU_LABELS[selectedInstance?.grau] || selectedInstance?.grau}
            </p>
          </div>
        </div>
      </div>

      {instances.source_limited && (
        <div className="flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
          <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
          <span>{instances.diagnostic_note || 'A fonte nao retornou todas as instancias esperadas.'}</span>
        </div>
      )}

      <div className={`grid grid-cols-1 ${gridCols} gap-3`}>
        {slots.map((slot) => {
          const isActive = selectedInstance?.index === slot.instance.index;
          return (
            <button
              key={slot.grau}
              type="button"
              onClick={() => handleSelect(slot.instance)}
              className={`rounded-xl border p-3 text-left transition-colors ${
                isActive
                  ? 'border-purple-500 bg-purple-100 shadow-sm'
                  : 'border-purple-200 bg-white hover:border-purple-400 hover:bg-purple-50'
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <span
                  className={`inline-flex items-center rounded px-2 py-0.5 text-[11px] font-bold ${
                    ['G1', 'JE'].includes(slot.grau)
                      ? 'bg-blue-100 text-blue-700'
                      : ['G2', 'TR'].includes(slot.grau)
                      ? 'bg-purple-100 text-purple-700'
                      : 'bg-amber-100 text-amber-700'
                  }`}
                >
                  {GRAU_LABELS[slot.grau]}
                </span>
                {isActive && <span className="text-[11px] font-semibold text-purple-700">Selecionada</span>}
              </div>

              <p className="mt-2 text-sm font-medium text-gray-900 flex items-center gap-1">
                <MapPin className="h-3 w-3 text-gray-400" />
                {slot.instance.orgao_julgador || 'Orgao nao informado'}
              </p>

              {slot.instance.latest_movement_at && (
                <p className="mt-1 text-xs text-gray-500 flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  Ultimo mov.:{' '}
                  {format(new Date(slot.instance.latest_movement_at), 'dd/MM/yyyy', { locale: ptBR })}
                </p>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

InstanceSelector.propTypes = {
  processNumber: PropTypes.string.isRequired,
  onInstanceChange: PropTypes.func,
  meta: PropTypes.shape({
    instances_count: PropTypes.number,
    selected_index: PropTypes.number,
    source_limited: PropTypes.bool,
    diagnostic_note: PropTypes.string,
    missing_expected_instances: PropTypes.arrayOf(PropTypes.string),
    instances: PropTypes.arrayOf(
      PropTypes.shape({
        index: PropTypes.number,
        grau: PropTypes.string,
        tribunal: PropTypes.string,
        orgao_julgador: PropTypes.string,
        latest_movement_at: PropTypes.string,
        updated_at: PropTypes.string,
      })
    ),
  }),
};

export default InstanceSelector;

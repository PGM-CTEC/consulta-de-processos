import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Layers, ChevronDown, MapPin, Calendar } from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

/**
 * Componente para selecionar entre múltiplas instâncias de um processo
 */
const InstanceSelector = ({ processNumber, onInstanceChange, meta }) => {
  const [instances, setInstances] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    if (meta && typeof meta === 'object') {
      const list = Array.isArray(meta.instances) ? meta.instances : [];
      const count = typeof meta.instances_count === 'number' ? meta.instances_count : list.length;
      setInstances({ instances: list, instances_count: count, selected_index: meta.selected_index || 0 });
      setSelectedIndex(meta.selected_index || 0);
      setLoading(false);
      return;
    }
    fetchInstances();
  }, [processNumber, meta]);

  const fetchInstances = async () => {
    try {
      const response = await fetch(`/processes/${processNumber}/instances`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      setInstances(data && typeof data === 'object' ? data : { instances: [], instances_count: 0 });
      setLoading(false);
    } catch (error) {
      console.error('Error fetching instances:', error);
      setInstances({ instances: [], instances_count: 0 });
      setLoading(false);
    }
  };

  const handleSelect = (index) => {
    const list = Array.isArray(instances?.instances) ? instances.instances : [];
    if (!list[index]) return;
    setSelectedIndex(index);
    setShowDropdown(false);
    if (onInstanceChange) {
      onInstanceChange(list[index]);
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

  const currentInstance = list[selectedIndex] || list[0];
  const grauLabels = {
    'G1': '1ª Instância',
    'G2': '2ª Instância',
    'SUP': 'Tribunais Superiores',
    'JE': 'Juizado Especial'
  };

  return (
    <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-xl p-4 mb-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-purple-600 p-2 rounded-lg">
            <Layers className="h-5 w-5 text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-purple-900">Múltiplas Instâncias Disponíveis</p>
            <p className="text-xs text-purple-600">
              {instances.instances_count} instâncias encontradas • Mostrando: {grauLabels[currentInstance.grau] || currentInstance.grau}
            </p>
          </div>
        </div>

        <div className="relative">
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="flex items-center space-x-2 px-4 py-2 bg-white border border-purple-300 rounded-lg hover:bg-purple-50 transition-colors font-medium text-sm text-purple-900 shadow-sm"
          >
            <span>Trocar Instância</span>
            <ChevronDown className={`h-4 w-4 transition-transform ${showDropdown ? 'rotate-180' : ''}`} />
          </button>

          {showDropdown && (
              <div className="absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-xl shadow-2xl z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
              {list.map((inst, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelect(idx)}
                  className={`w-full text-left px-4 py-3 hover:bg-purple-50 transition-colors border-b border-gray-100 last:border-b-0 ${
                    idx === selectedIndex ? 'bg-purple-100' : ''
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                          inst.grau === 'G1' ? 'bg-blue-100 text-blue-700' :
                          inst.grau === 'G2' ? 'bg-purple-100 text-purple-700' :
                          'bg-amber-100 text-amber-700'
                        }`}>
                          {grauLabels[inst.grau] || inst.grau}
                        </span>
                        {idx === selectedIndex && (
                          <span className="text-xs text-purple-600 font-medium">(atual)</span>
                        )}
                      </div>
                      <p className="text-sm font-medium text-gray-900 flex items-center mt-1">
                        <MapPin className="h-3 w-3 mr-1 text-gray-400" />
                        {inst.orgao_julgador}
                      </p>
                      {inst.latest_movement_at && (
                        <p className="text-xs text-gray-500 flex items-center mt-1">
                          <Calendar className="h-3 w-3 mr-1" />
                          Último mov.: {format(new Date(inst.latest_movement_at), "dd/MM/yyyy", { locale: ptBR })}
                        </p>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
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
    instances: PropTypes.arrayOf(
      PropTypes.shape({
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

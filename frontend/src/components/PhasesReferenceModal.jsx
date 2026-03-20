import { useEffect, useRef } from 'react';
import { X } from 'lucide-react';
import PhaseReference from './PhaseReference';

export default function PhasesReferenceModal({ onClose }) {
  const closeRef = useRef(null);

  useEffect(() => {
    const handle = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handle);
    closeRef.current?.focus();
    return () => document.removeEventListener('keydown', handle);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      aria-hidden="false"
    >
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Dialog */}
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="phases-modal-title"
        className="relative z-10 bg-white dark:bg-gray-900 rounded-2xl shadow-2xl
                   w-full max-w-4xl max-h-[90vh] overflow-y-auto mx-4"
      >
        {/* Header fixo */}
        <div className="sticky top-0 z-10 flex items-center justify-between
                        bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700
                        px-6 py-4 rounded-t-2xl">
          <h2 id="phases-modal-title"
              className="text-lg font-bold text-gray-900 dark:text-white">
            Fases Processuais
          </h2>
          <button
            ref={closeRef}
            onClick={onClose}
            aria-label="Fechar"
            className="p-1 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200
                       hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors
                       focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Conteúdo */}
        <div className="p-2">
          <PhaseReference />
        </div>
      </div>
    </div>
  );
}

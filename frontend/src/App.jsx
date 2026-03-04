import { useState, lazy, Suspense } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { Search, Database, Layers, BarChart3, Sun, Moon } from 'lucide-react';
import SearchProcess from './components/SearchProcess';
import LoadingFallback from './components/LoadingFallback';
import FeedbackButton from './components/FeedbackButton';
import HistoryTab from './components/HistoryTab'; // Import direto para evitar erro com React 19
import { searchProcess } from './services/api';
import { useLabels } from './hooks/useLabels';
import { useTheme } from './hooks/useTheme';

// Lazy-loaded tab components — loaded only when the user navigates to that tab.
// This splits the bundle into separate chunks, reducing initial load time.
const ProcessDetails = lazy(() => import('./components/ProcessDetails'));
const BulkSearch = lazy(() => import('./components/BulkSearch'));
const Dashboard = lazy(() => import('./components/Dashboard'));
const PhaseReference = lazy(() => import('./components/PhaseReference'));

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('single'); // 'single' | 'bulk' | 'analytics' | 'history'
  const [showPhasesModal, setShowPhasesModal] = useState(false);
  const { labels, loading: labelsLoading } = useLabels();
  const { isDark, toggleTheme } = useTheme();

  if (labelsLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const handleSearch = async (number) => {
    setLoading(true);
    setData(null);
    try {
      const result = await searchProcess(number);
      setData(result);
      toast.success(labels.search.success);
    } catch (error) {
      console.error(error);
      const msg = error.response?.data?.detail || labels.search.error;
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleViewFromHistory = (processData) => {
    // Muda para a aba "Consulta Individual" e exibe os dados
    setActiveTab('single');
    setData(processData);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 flex flex-col">
      {/* Skip to main content link for accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-indigo-600 focus:text-white focus:rounded-lg focus:shadow-lg"
      >
        Pular para conteúdo principal
      </a>

      <Toaster position="top-right" toastOptions={{ ariaLive: 'polite' }} />

      {/* Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700 sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 h-20 sm:px-6 lg:px-8 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-indigo-600 rounded-lg p-2 shadow-md shadow-indigo-100">
              <Database className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-gray-900 dark:text-white tracking-tight leading-none">
                {labels.app.title.split(' ')[0]}<span className="text-indigo-600 dark:text-indigo-400">{labels.app.title.split(' ')[1] || ''}</span>
              </h1>
              <p className="text-[10px] text-indigo-600 dark:text-indigo-400 font-bold uppercase tracking-widest leading-none mt-1">{labels.app.subtitle}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <nav
              className="flex bg-gray-100 dark:bg-gray-700 p-1 rounded-xl border border-gray-200 dark:border-gray-600"
              role="tablist"
              aria-label="Tipo de consulta"
            >
              {[
                { id: 'single',    label: labels.nav.single,    icon: Search    },
                { id: 'bulk',      label: labels.nav.bulk,      icon: Layers    },
                { id: 'analytics', label: labels.nav.analytics, icon: BarChart3 },
                { id: 'history',   label: labels.nav.history,   icon: Database  },
              ].map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id)}
                  role="tab"
                  aria-selected={activeTab === id}
                  aria-controls={`tab-panel-${id}`}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-bold transition-all
                    focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2
                    ${activeTab === id
                      ? 'bg-white dark:bg-gray-800 text-indigo-600 shadow-sm'
                      : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
                    }`}
                >
                  <Icon className="h-4 w-4" aria-hidden="true" />
                  <span>{label}</span>
                </button>
              ))}
            </nav>

            {/* Toggle tema */}
            <button
              onClick={toggleTheme}
              aria-label="Alternar tema"
              aria-pressed={isDark}
              className="p-2 rounded-lg text-gray-500 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main id="main-content" className="flex-grow py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto space-y-12">

          {activeTab === 'single' && (
            <div
              id="tab-panel-single"
              role="tabpanel"
              aria-labelledby="tab-single"
              className="space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-700"
            >
              <div className="text-center space-y-4">
                <h2 className="text-4xl font-extrabold text-gray-900 dark:text-white sm:text-5xl">
                  {labels.home.heroTitle} <br />
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600 dark:from-indigo-400 dark:to-violet-400">
                    {labels.home.heroHighlight}
                  </span>
                </h2>
                <p className="max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-400">
                  {labels.home.heroSubtitle}
                </p>
              </div>

              <SearchProcess onSearch={handleSearch} loading={loading} labels={labels} onShowPhases={() => setShowPhasesModal(true)} />

              {data && (
                <Suspense fallback={<LoadingFallback message="Carregando detalhes do processo..." />}>
                  <ProcessDetails data={data} />
                </Suspense>
              )}
            </div>
          )}

          {activeTab === 'bulk' && (
            <div
              id="tab-panel-bulk"
              role="tabpanel"
              aria-labelledby="tab-bulk"
              className="animate-in fade-in slide-in-from-bottom-4 duration-700"
            >
              <Suspense fallback={<LoadingFallback message="Carregando consulta em lote..." />}>
                <BulkSearch onShowPhases={() => setShowPhasesModal(true)} />
              </Suspense>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div
              id="tab-panel-analytics"
              role="tabpanel"
              aria-labelledby="tab-analytics"
              className="animate-in fade-in slide-in-from-bottom-4 duration-700"
            >
              <Suspense fallback={<LoadingFallback message="Carregando dashboard..." />}>
                <Dashboard />
              </Suspense>
            </div>
          )}

          {activeTab === 'history' && (
            <div
              id="tab-panel-history"
              role="tabpanel"
              aria-labelledby="tab-history"
              className="animate-in fade-in slide-in-from-bottom-4 duration-700"
            >
              <HistoryTab labels={labels} onProcessView={handleViewFromHistory} />
            </div>
          )}

        </div>
      </main>

      {showPhasesModal && (
        <Suspense fallback={null}>
          <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" onClick={() => setShowPhasesModal(false)}>
            <div className="bg-white rounded-2xl shadow-2xl max-w-6xl max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
              <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between z-10">
                <h2 className="text-xl font-bold text-gray-900">Referência de Fases</h2>
                <button
                  onClick={() => setShowPhasesModal(false)}
                  className="text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded-lg p-2"
                  aria-label="Fechar modal"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <PhaseReference />
            </div>
          </div>
        </Suspense>
      )}

      <FeedbackButton />

      {/* Footer */}
      <footer className="bg-white dark:bg-slate-800 border-t border-gray-200 dark:border-slate-700 mt-auto">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 text-center sm:flex sm:justify-between sm:items-center">
          <p className="text-gray-400 dark:text-gray-500 text-sm">
            {labels.app.footerText}
          </p>
          <div className="mt-4 sm:mt-0 flex justify-center space-x-6">
            <span className="inline-flex items-center text-xs font-semibold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 px-2 py-1 rounded">
              {labels.app.statusOnline}
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

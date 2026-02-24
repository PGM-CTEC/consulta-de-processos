import { useState } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { Search, Database, Layers, BarChart3, Settings } from 'lucide-react';
import SearchProcess from './components/SearchProcess';
import ProcessDetails from './components/ProcessDetails';
import BulkSearch from './components/BulkSearch';
import Dashboard from './components/Dashboard';
import PerformanceDashboard from './components/PerformanceDashboard';
import SettingsComponent from './components/Settings';
import { searchProcess } from './services/api';
import { useLabels } from './hooks/useLabels';
import HistoryTab from './components/HistoryTab';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('single'); // 'single', 'bulk', 'analytics', 'performance', 'history' or 'settings'
  const { labels, loading: labelsLoading } = useLabels();

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

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Skip to main content link for accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-indigo-600 focus:text-white focus:rounded-lg focus:shadow-lg"
      >
        Pular para conteúdo principal
      </a>

      <Toaster position="top-right" toastOptions={{ ariaLive: 'polite' }} />

      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 h-20 sm:px-6 lg:px-8 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-indigo-600 rounded-lg p-2 shadow-md shadow-indigo-100">
              <Database className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-gray-900 tracking-tight leading-none">
                {labels.app.title.split(' ')[0]}<span className="text-indigo-600">{labels.app.title.split(' ')[1] || ''}</span>
              </h1>
              <p className="text-[10px] text-indigo-600 font-bold uppercase tracking-widest leading-none mt-1">{labels.app.subtitle}</p>
            </div>
          </div>

          <nav className="flex bg-gray-100 p-1 rounded-xl border border-gray-200" role="tablist" aria-label="Tipo de consulta">
            <button
              onClick={() => setActiveTab('single')}
              role="tab"
              aria-selected={activeTab === 'single'}
              aria-controls="tab-panel-single"
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-bold transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${activeTab === 'single'
                ? 'bg-white text-indigo-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
                }`}
            >
              <Search className="h-4 w-4" aria-hidden="true" />
              <span>{labels.nav.single}</span>
            </button>
            <button
              onClick={() => setActiveTab('bulk')}
              role="tab"
              aria-selected={activeTab === 'bulk'}
              aria-controls="tab-panel-bulk"
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-bold transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${activeTab === 'bulk'
                ? 'bg-white text-indigo-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
                }`}
            >
              <Layers className="h-4 w-4" aria-hidden="true" />
              <span>{labels.nav.bulk}</span>
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              role="tab"
              aria-selected={activeTab === 'analytics'}
              aria-controls="tab-panel-analytics"
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-bold transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${activeTab === 'analytics'
                ? 'bg-white text-indigo-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
                }`}
            >
              <BarChart3 className="h-4 w-4" aria-hidden="true" />
              <span>{labels.nav.analytics}</span>
            </button>
            <button
              onClick={() => setActiveTab('history')}
              role="tab"
              aria-selected={activeTab === 'history'}
              aria-controls="tab-panel-history"
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-bold transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${activeTab === 'history'
                ? 'bg-white text-indigo-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
                }`}
            >
              <Database className="h-4 w-4" aria-hidden="true" />
              <span>{labels.nav.history}</span>
            </button>
            <button
              onClick={() => setActiveTab('performance')}
              role="tab"
              aria-selected={activeTab === 'performance'}
              aria-controls="tab-panel-performance"
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-bold transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${activeTab === 'performance'
                ? 'bg-white text-indigo-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
                }`}
            >
              <BarChart3 className="h-4 w-4" aria-hidden="true" />
              <span>Performance</span>
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              role="tab"
              aria-selected={activeTab === 'settings'}
              aria-controls="tab-panel-settings"
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-bold transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${activeTab === 'settings'
                ? 'bg-white text-indigo-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
                }`}
            >
              <Settings className="h-4 w-4" aria-hidden="true" />
              <span>{labels.nav.settings}</span>
            </button>
          </nav>
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
                <h2 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
                  {labels.home.heroTitle} <br />
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">
                    {labels.home.heroHighlight}
                  </span>
                </h2>
                <p className="max-w-2xl mx-auto text-xl text-gray-500">
                  {labels.home.heroSubtitle}
                </p>
              </div>

              <SearchProcess onSearch={handleSearch} loading={loading} labels={labels} />

              {data && <ProcessDetails data={data} />}
            </div>
          )}

          {activeTab === 'bulk' && (
            <div
              id="tab-panel-bulk"
              role="tabpanel"
              aria-labelledby="tab-bulk"
              className="animate-in fade-in slide-in-from-bottom-4 duration-700"
            >
              <BulkSearch />
            </div>
          )}

          {activeTab === 'analytics' && (
            <div
              id="tab-panel-analytics"
              role="tabpanel"
              aria-labelledby="tab-analytics"
              className="animate-in fade-in slide-in-from-bottom-4 duration-700"
            >
              <Dashboard />
            </div>
          )}

          {activeTab === 'history' && (
            <div
              id="tab-panel-history"
              role="tabpanel"
              aria-labelledby="tab-history"
              className="animate-in fade-in slide-in-from-bottom-4 duration-700"
            >
              <HistoryTab labels={labels} />
            </div>
          )}

          {activeTab === 'performance' && (
            <div
              id="tab-panel-performance"
              role="tabpanel"
              aria-labelledby="tab-performance"
              className="animate-in fade-in slide-in-from-bottom-4 duration-700"
            >
              <PerformanceDashboard />
            </div>
          )}

          {activeTab === 'settings' && (
            <div
              id="tab-panel-settings"
              role="tabpanel"
              aria-labelledby="tab-settings"
              className="animate-in fade-in slide-in-from-bottom-4 duration-700"
            >
              <SettingsComponent />
            </div>
          )}

        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 text-center sm:flex sm:justify-between sm:items-center">
          <p className="text-gray-400 text-sm">
            {labels.app.footerText}
          </p>
          <div className="mt-4 sm:mt-0 flex justify-center space-x-6">
            <span className="inline-flex items-center text-xs font-semibold text-indigo-600 bg-indigo-50 px-2 py-1 rounded">
              {labels.app.statusOnline}
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

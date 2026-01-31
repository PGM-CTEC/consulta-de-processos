import { useState } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { Search, Database, Layers } from 'lucide-react';
import SearchProcess from './components/SearchProcess';
import ProcessDetails from './components/ProcessDetails';
import BulkSearch from './components/BulkSearch';
import { searchProcess } from './services/api';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('single'); // 'single' or 'bulk'

  const handleSearch = async (number) => {
    setLoading(true);
    setData(null);
    try {
      const result = await searchProcess(number);
      setData(result);
      toast.success('Processo encontrado!');
    } catch (error) {
      console.error(error);
      const msg = error.response?.data?.detail || 'Erro ao buscar processo. Verifique o número ou tente novamente.';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Toaster position="top-right" />

      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 h-20 sm:px-6 lg:px-8 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-indigo-600 rounded-lg p-2 shadow-md shadow-indigo-100">
              <Database className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-gray-900 tracking-tight leading-none">
                Consulta<span className="text-indigo-600">Processual</span>
              </h1>
              <p className="text-[10px] text-indigo-600 font-bold uppercase tracking-widest leading-none mt-1">DataJud Intelligence</p>
            </div>
          </div>

          <nav className="flex bg-gray-100 p-1 rounded-xl border border-gray-200">
            <button
              onClick={() => setActiveTab('single')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'single'
                  ? 'bg-white text-indigo-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
                }`}
            >
              <Search className="h-4 w-4" />
              <span>Consulta Individual</span>
            </button>
            <button
              onClick={() => setActiveTab('bulk')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'bulk'
                  ? 'bg-white text-indigo-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
                }`}
            >
              <Layers className="h-4 w-4" />
              <span>Busca em Lote</span>
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto space-y-12">

          {activeTab === 'single' ? (
            <div className="space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
              <div className="text-center space-y-4">
                <h2 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
                  Consulte processos em <br />
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">
                    tempo real
                  </span>
                </h2>
                <p className="max-w-2xl mx-auto text-xl text-gray-500">
                  Acesse dados unificados do Poder Judiciário (DataJud) de forma simples e rápida.
                </p>
              </div>

              <SearchProcess onSearch={handleSearch} loading={loading} />

              {data && <ProcessDetails data={data} />}
            </div>
          ) : (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
              <BulkSearch />
            </div>
          )}

        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 text-center sm:flex sm:justify-between sm:items-center">
          <p className="text-gray-400 text-sm">
            © 2026 Consulta Processual. Dados providos por DataJud/CNJ.
          </p>
          <div className="mt-4 sm:mt-0 flex justify-center space-x-6">
            <span className="inline-flex items-center text-xs font-semibold text-indigo-600 bg-indigo-50 px-2 py-1 rounded">
              Status: Online
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

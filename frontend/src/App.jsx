import { useState } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import SearchProcess from './components/SearchProcess';
import ProcessDetails from './components/ProcessDetails';
import { searchProcess } from './services/api';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

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
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-indigo-600 rounded-lg p-2">
              {/* Simple Icon placeholder */}
              <div className="h-4 w-4 bg-white rounded-full opacity-50"></div>
            </div>
            <h1 className="text-xl font-bold text-gray-900 tracking-tight">
              Consulta<span className="text-indigo-600">Processual</span>
            </h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto space-y-12">

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
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-gray-400 text-sm">
            © 2026 Consulta Processual. Dados providos por DataJud/CNJ.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;

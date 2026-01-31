import React, { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';

export default function SearchProcess({ onSearch, loading }) {
    const [number, setNumber] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (number.trim()) {
            onSearch(number.trim());
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto p-6">
            <form onSubmit={handleSubmit} className="relative flex items-center">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-gray-400" />
                </div>
                <input
                    type="text"
                    value={number}
                    onChange={(e) => setNumber(e.target.value)}
                    placeholder="Digite o número do processo (CNJ)..."
                    className="block w-full pl-10 pr-12 py-4 text-lg border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all shadow-sm"
                    disabled={loading}
                />
                <button
                    type="submit"
                    disabled={loading || !number}
                    className="absolute right-2 top-2 bottom-2 bg-indigo-600 text-white px-6 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : 'Consultar'}
                </button>
            </form>
            <p className="mt-3 text-sm text-gray-400 text-center">
                Ex: 5000000-00.2024.8.10.0000
            </p>
        </div>
    );
}

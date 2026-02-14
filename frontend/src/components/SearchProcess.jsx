import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Search, Loader2 } from 'lucide-react';

function SearchProcess({ onSearch, loading, labels }) {
    const [number, setNumber] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (number.trim()) {
            onSearch(number.trim());
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto p-6">
            <form onSubmit={handleSubmit} className="relative flex items-center" role="search">
                <label htmlFor="process-number-input" className="sr-only">
                    {labels.search.placeholder}
                </label>
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none" aria-hidden="true">
                    <Search className="h-5 w-5 text-gray-400" />
                </div>
                <input
                    id="process-number-input"
                    type="text"
                    value={number}
                    onChange={(e) => setNumber(e.target.value)}
                    placeholder={labels.search.placeholder}
                    aria-label={labels.search.placeholder}
                    aria-describedby="process-number-help"
                    className="block w-full pl-10 pr-12 py-4 text-lg border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all shadow-sm"
                    disabled={loading}
                    autoComplete="off"
                />
                <button
                    type="submit"
                    disabled={loading || !number}
                    aria-label={loading ? labels.search.loading : labels.search.button}
                    className="absolute right-2 top-2 bottom-2 bg-indigo-600 text-white px-6 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                >
                    {loading ? (
                        <>
                            <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />
                            <span className="sr-only">{labels.search.loading}</span>
                        </>
                    ) : (
                        labels.search.button
                    )}
                </button>
            </form>
            <p id="process-number-help" className="mt-3 text-sm text-gray-400 text-center">
                Ex: 5000000-00.2024.8.10.0000
            </p>
        </div>
    );
}

SearchProcess.propTypes = {
    onSearch: PropTypes.func.isRequired,
    loading: PropTypes.bool.isRequired,
};

export default SearchProcess;

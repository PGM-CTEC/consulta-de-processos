import React from 'react';
import PropTypes from 'prop-types';
import { Search, Loader2 } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { standardSchemaResolver } from '@hookform/resolvers/standard-schema';
import { searchProcessSchema } from '../lib/validationSchemas';
import { trackSearch } from '../lib/analytics';

function SearchProcess({ onSearch, loading, labels }) {
    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm({
        resolver: standardSchemaResolver(searchProcessSchema),
        defaultValues: { number: '' },
    });

    const onSubmit = ({ number }) => {
        trackSearch('single', true);
        onSearch(number.trim());
    };

    return (
        <div className="w-full max-w-2xl mx-auto p-6">
            <form onSubmit={handleSubmit(onSubmit)} className="relative flex flex-col" role="search">
                <div className="relative flex items-center">
                    <label htmlFor="process-number-input" className="sr-only">
                        {labels.search.placeholder}
                    </label>
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none" aria-hidden="true">
                        <Search className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                        id="process-number-input"
                        type="text"
                        {...register('number')}
                        placeholder={labels.search.placeholder}
                        aria-label={labels.search.placeholder}
                        aria-describedby="process-number-help"
                        aria-invalid={!!errors.number}
                        className={`block w-full pl-10 pr-12 py-4 text-lg border-2 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all shadow-sm ${errors.number ? 'border-red-400' : 'border-gray-200'}`}
                        disabled={loading}
                        autoComplete="off"
                    />
                    <button
                        type="submit"
                        disabled={loading}
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
                </div>
                {errors.number && (
                    <p role="alert" className="mt-2 text-sm text-red-500 font-medium text-center">
                        {errors.number.message}
                    </p>
                )}
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

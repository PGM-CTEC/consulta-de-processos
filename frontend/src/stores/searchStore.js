import { create } from 'zustand';

/**
 * Search store for managing search history and current search state
 * Replaces prop drilling of search-related state
 */
export const useSearchStore = create((set, get) => ({
  searchHistory: [],
  currentSearch: null,
  recentSearches: [],

  // Add to search history
  addSearch: (searchTerm, type = 'single') => {
    set((state) => {
      const newSearch = {
        id: Date.now(),
        term: searchTerm,
        type,
        timestamp: new Date(),
      };
      return {
        currentSearch: newSearch,
        searchHistory: [newSearch, ...state.searchHistory].slice(0, 50), // Keep last 50
        recentSearches: [newSearch, ...state.recentSearches].slice(0, 10), // Keep last 10
      };
    });
  },

  // Clear search history
  clearHistory: () => set({ searchHistory: [], recentSearches: [] }),

  // Set current search
  setCurrentSearch: (search) => set({ currentSearch: search }),

  // Get search by ID
  getSearchById: (id) => {
    const { searchHistory } = get();
    return searchHistory.find((s) => s.id === id);
  },

  // Remove search from history
  removeFromHistory: (id) => {
    set((state) => ({
      searchHistory: state.searchHistory.filter((s) => s.id !== id),
      recentSearches: state.recentSearches.filter((s) => s.id !== id),
    }));
  },
}));

export default useSearchStore;

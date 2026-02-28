import { describe, it, expect, beforeEach } from 'vitest';
import { useSearchStore } from '../stores/searchStore';
import { useSettingsStore } from '../stores/settingsStore';

describe('Zustand Stores', () => {
  describe('SearchStore', () => {
    beforeEach(() => {
      const initialState = {
        searchHistory: [],
        currentSearch: null,
        recentSearches: [],
      };
      useSearchStore.setState(initialState);
    });

    it('should add search to history', () => {
      useSearchStore.getState().addSearch('0001234-56.2020.1.26.0100', 'single');
      const { searchHistory } = useSearchStore.getState();

      expect(searchHistory).toHaveLength(1);
      expect(searchHistory[0].term).toBe('0001234-56.2020.1.26.0100');
      expect(searchHistory[0].type).toBe('single');
    });

    it('should set current search', () => {
      const search = { id: 1, term: 'test', type: 'single' };
      useSearchStore.getState().setCurrentSearch(search);

      expect(useSearchStore.getState().currentSearch).toEqual(search);
    });

    it('should clear search history', () => {
      useSearchStore.getState().addSearch('search1', 'single');
      useSearchStore.getState().addSearch('search2', 'bulk');
      useSearchStore.getState().clearHistory();

      const { searchHistory, recentSearches } = useSearchStore.getState();
      expect(searchHistory).toHaveLength(0);
      expect(recentSearches).toHaveLength(0);
    });

    it('should get search by ID', () => {
      useSearchStore.getState().addSearch('test-search', 'single');
      const { searchHistory } = useSearchStore.getState();
      const id = searchHistory[0].id;

      const found = useSearchStore.getState().getSearchById(id);
      expect(found).toBeDefined();
      expect(found.term).toBe('test-search');
    });

    it('should remove search from history and recents', () => {
      useSearchStore.getState().addSearch('search1', 'single');
      const id1 = useSearchStore.getState().searchHistory[0].id;

      useSearchStore.getState().removeFromHistory(id1);

      expect(useSearchStore.getState().searchHistory).toHaveLength(0);
      expect(useSearchStore.getState().recentSearches).toHaveLength(0);
    });

    it('should keep max 50 items in search history', () => {
      for (let i = 0; i < 60; i++) {
        useSearchStore.getState().addSearch(`search${i}`, 'single');
      }

      expect(useSearchStore.getState().searchHistory).toHaveLength(50);
    });

    it('should keep max 10 items in recent searches', () => {
      for (let i = 0; i < 15; i++) {
        useSearchStore.getState().addSearch(`search${i}`, 'single');
      }

      expect(useSearchStore.getState().recentSearches).toHaveLength(10);
    });
  });

  describe('SettingsStore', () => {
    beforeEach(() => {
      useSettingsStore.setState({
        dbDriver: 'postgresql',
        dbHost: 'localhost',
        dbPort: 5432,
        dbUser: '',
        dbPassword: '',
        dbName: 'consulta_processo',
        customQuery: '',
        theme: 'light',
        language: 'pt-BR',
        itemsPerPage: 25,
        enableNotifications: true,
      });
    });

    it('should update database settings', () => {
      useSettingsStore.getState().setDatabaseSettings({
        dbHost: 'remote-host',
        dbPort: 5433,
      });

      const state = useSettingsStore.getState();
      expect(state.dbHost).toBe('remote-host');
      expect(state.dbPort).toBe(5433);
    });

    it('should update single setting', () => {
      useSettingsStore.getState().updateSetting('theme', 'dark');

      expect(useSettingsStore.getState().theme).toBe('dark');
    });

    it('should reset to default settings', () => {
      useSettingsStore.getState().updateSetting('itemsPerPage', 50);
      useSettingsStore.getState().updateSetting('theme', 'dark');
      useSettingsStore.getState().resetSettings();

      const state = useSettingsStore.getState();
      expect(state.itemsPerPage).toBe(25);
      expect(state.theme).toBe('light');
      expect(state.dbHost).toBe('localhost');
    });

    it('should get all settings', () => {
      const settings = useSettingsStore.getState().getSettings();

      expect(settings).toHaveProperty('dbDriver');
      expect(settings).toHaveProperty('theme');
      expect(settings).toHaveProperty('language');
      expect(settings).toHaveProperty('itemsPerPage');
    });

    it('should have default values', () => {
      const state = useSettingsStore.getState();

      expect(state.dbDriver).toBe('postgresql');
      expect(state.dbHost).toBe('localhost');
      expect(state.dbPort).toBe(5432);
      expect(state.theme).toBe('light');
      expect(state.language).toBe('pt-BR');
      expect(state.itemsPerPage).toBe(25);
    });
  });
});

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * Settings store for managing user preferences and configuration
 * Persists to localStorage to maintain user settings across sessions
 */
export const useSettingsStore = create(
  persist(
    (set, get) => ({
      // Database settings
      dbDriver: 'postgresql',
      dbHost: 'localhost',
      dbPort: 5432,
      dbUser: '',
      dbPassword: '',
      dbName: 'consulta_processo',
      customQuery: '',

      // UI preferences
      theme: 'light',
      language: 'pt-BR',
      itemsPerPage: 25,
      enableNotifications: true,

      // Update database settings
      setDatabaseSettings: (settings) => set((state) => ({
        ...state,
        ...settings,
      })),

      // Update a single setting
      updateSetting: (key, value) => set((state) => ({
        [key]: value,
      })),

      // Reset to defaults
      resetSettings: () => set({
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
      }),

      // Get all settings as object
      getSettings: () => get(),
    }),
    {
      name: 'consulta-processo-settings', // localStorage key
      partialize: (state) => ({
        // Only persist non-sensitive data
        theme: state.theme,
        language: state.language,
        itemsPerPage: state.itemsPerPage,
        enableNotifications: state.enableNotifications,
      }),
    }
  )
);

export default useSettingsStore;

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  trackEvent,
  trackSearch,
  trackBulkUpload,
  trackExport,
  trackProcessView,
  trackConversion,
} from '../lib/analytics';

describe('Analytics', () => {
  beforeEach(() => {
    // Mock the Plausible global
    window.plausible = vi.fn();
  });

  afterEach(() => {
    delete window.plausible;
  });

  describe('trackEvent', () => {
    it('should call plausible with event name and props', () => {
      trackEvent('Custom Event', { key: 'value' });

      expect(window.plausible).toHaveBeenCalledWith('Custom Event', {
        props: { key: 'value' },
      });
    });

    it('should call plausible with empty props if none provided', () => {
      trackEvent('Simple Event');

      expect(window.plausible).toHaveBeenCalledWith('Simple Event', {
        props: {},
      });
    });

    it('should handle missing plausible gracefully', () => {
      delete window.plausible;

      expect(() => trackEvent('Test Event')).not.toThrow();
    });

    it('should handle plausible errors gracefully', () => {
      window.plausible = vi.fn(() => {
        throw new Error('Plausible error');
      });

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      trackEvent('Test Event');

      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
  });

  describe('trackSearch', () => {
    it('should track single search with success', () => {
      trackSearch('single', true);

      expect(window.plausible).toHaveBeenCalledWith('Search', {
        props: {
          type: 'single',
          success: 'true',
        },
      });
    });

    it('should track bulk search with failure', () => {
      trackSearch('bulk', false);

      expect(window.plausible).toHaveBeenCalledWith('Search', {
        props: {
          type: 'bulk',
          success: 'false',
        },
      });
    });

    it('should default to single search with success', () => {
      trackSearch();

      expect(window.plausible).toHaveBeenCalledWith('Search', {
        props: {
          type: 'single',
          success: 'true',
        },
      });
    });
  });

  describe('trackBulkUpload', () => {
    it('should track bulk upload with correct props', () => {
      trackBulkUpload(1024, 5, true);

      expect(window.plausible).toHaveBeenCalledWith('Bulk Upload', {
        props: {
          fileSize: '1024',
          processCount: '5',
          success: 'true',
        },
      });
    });

    it('should track failed bulk upload', () => {
      trackBulkUpload(512, 3, false);

      expect(window.plausible).toHaveBeenCalledWith('Bulk Upload', {
        props: {
          fileSize: '512',
          processCount: '3',
          success: 'false',
        },
      });
    });
  });

  describe('trackExport', () => {
    it('should track export with CSV format', () => {
      trackExport('CSV', 10, true);

      expect(window.plausible).toHaveBeenCalledWith('Export', {
        props: {
          format: 'CSV',
          recordCount: '10',
          success: 'true',
        },
      });
    });

    it('should track export with PDF format', () => {
      trackExport('PDF', 5, true);

      expect(window.plausible).toHaveBeenCalledWith('Export', {
        props: {
          format: 'PDF',
          recordCount: '5',
          success: 'true',
        },
      });
    });

    it('should default to CSV format', () => {
      trackExport(undefined, 20, true);

      expect(window.plausible).toHaveBeenCalledWith('Export', {
        props: {
          format: 'CSV',
          recordCount: '20',
          success: 'true',
        },
      });
    });
  });

  describe('trackProcessView', () => {
    it('should track process view with process ID', () => {
      trackProcessView('0001234-56.2020.1.26.0100');

      expect(window.plausible).toHaveBeenCalledWith('Process View', {
        props: {
          processId: '0001234-56.2020.1.26.0100',
        },
      });
    });
  });

  describe('trackConversion', () => {
    it('should track conversion funnel steps', () => {
      trackConversion('search_results');

      expect(window.plausible).toHaveBeenCalledWith('Conversion', {
        props: {
          step: 'search_results',
        },
      });
    });

    it('should track another conversion step', () => {
      trackConversion('process_details_view');

      expect(window.plausible).toHaveBeenCalledWith('Conversion', {
        props: {
          step: 'process_details_view',
        },
      });
    });
  });
});

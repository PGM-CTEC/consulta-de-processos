/**
 * Analytics module for Plausible integration
 * Tracks user behavior: page views, searches, bulk uploads, exports
 */

/**
 * Track a custom event in Plausible
 * @param {string} eventName - Name of the event
 * @param {object} props - Event properties (optional)
 */
export function trackEvent(eventName, props = {}) {
  try {
    if (window.plausible) {
      window.plausible(eventName, { props });
    }
  } catch (error) {
    console.error(`Error tracking event "${eventName}":`, error);
  }
}

/**
 * Track a search event
 * @param {string} searchType - 'single' or 'bulk'
 * @param {boolean} success - Whether the search was successful
 */
export function trackSearch(searchType = 'single', success = true) {
  trackEvent('Search', {
    type: searchType,
    success: success.toString(),
  });
}

/**
 * Track a bulk upload event
 * @param {number} fileSize - Size of the uploaded file in bytes
 * @param {number} processCount - Number of processes in the upload
 * @param {boolean} success - Whether the upload was successful
 */
export function trackBulkUpload(fileSize, processCount, success = true) {
  trackEvent('Bulk Upload', {
    fileSize: fileSize.toString(),
    processCount: processCount.toString(),
    success: success.toString(),
  });
}

/**
 * Track an export event
 * @param {string} format - Export format (CSV, PDF, etc.)
 * @param {number} recordCount - Number of records exported
 * @param {boolean} success - Whether the export was successful
 */
export function trackExport(format = 'CSV', recordCount, success = true) {
  trackEvent('Export', {
    format,
    recordCount: recordCount.toString(),
    success: success.toString(),
  });
}

/**
 * Track process details view
 * @param {string} processId - The process number
 */
export function trackProcessView(processId) {
  trackEvent('Process View', {
    processId,
  });
}

/**
 * Track conversion funnel event (e.g., user reached results)
 * @param {string} step - Funnel step identifier
 */
export function trackConversion(step) {
  trackEvent('Conversion', {
    step,
  });
}

export default {
  trackEvent,
  trackSearch,
  trackBulkUpload,
  trackExport,
  trackProcessView,
  trackConversion,
};

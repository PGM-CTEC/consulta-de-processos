/**
 * Accessibility Utilities
 *
 * WCAG 2.1 AA Compliance helpers
 * - Color contrast checking
 * - ARIA label validation
 * - Keyboard navigation utilities
 */

/**
 * Calculate relative luminance of a color
 * @param {string} hex - Hex color code (e.g., #FFFFFF)
 * @returns {number} Luminance value (0-1)
 */
export function getRelativeLuminance(hex) {
    const rgb = parseInt(hex.slice(1), 16);
    const r = (rgb >> 16) & 255;
    const g = (rgb >> 8) & 255;
    const b = rgb & 255;

    // Normalize to 0-1 range
    const rNorm = r / 255;
    const gNorm = g / 255;
    const bNorm = b / 255;

    // Apply gamma correction
    const rLinear = rNorm <= 0.03928 ? rNorm / 12.92 : Math.pow((rNorm + 0.055) / 1.055, 2.4);
    const gLinear = gNorm <= 0.03928 ? gNorm / 12.92 : Math.pow((gNorm + 0.055) / 1.055, 2.4);
    const bLinear = bNorm <= 0.03928 ? bNorm / 12.92 : Math.pow((bNorm + 0.055) / 1.055, 2.4);

    // Calculate relative luminance
    return 0.2126 * rLinear + 0.7152 * gLinear + 0.0722 * bLinear;
}

/**
 * Calculate WCAG contrast ratio between two colors
 * @param {string} foreground - Hex color for foreground
 * @param {string} background - Hex color for background
 * @returns {number} Contrast ratio (1-21)
 */
export function getContrastRatio(foreground, background) {
    const l1 = getRelativeLuminance(foreground);
    const l2 = getRelativeLuminance(background);

    const lighter = Math.max(l1, l2);
    const darker = Math.min(l1, l2);

    return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Check if contrast ratio meets WCAG AA standard
 * @param {number} ratio - Contrast ratio
 * @param {boolean} isLargeText - Whether text is 18pt+ or 14pt+ bold
 * @returns {boolean} True if meets WCAG AA
 */
export function meetsWCAGAA(ratio, isLargeText = false) {
    // WCAG AA: 4.5:1 for normal text, 3:1 for large text
    return isLargeText ? ratio >= 3 : ratio >= 4.5;
}

/**
 * Validate ARIA label exists and is not empty
 * @param {HTMLElement} element - DOM element to check
 * @returns {boolean} True if element has valid ARIA label
 */
export function hasValidAriaLabel(element) {
    if (!element) return false;

    const ariaLabel = element.getAttribute('aria-label');
    const ariaLabelledBy = element.getAttribute('aria-labelledby');
    const textContent = element.textContent?.trim();

    return !!(
        (ariaLabel && ariaLabel.trim()) ||
        ariaLabelledBy ||
        textContent
    );
}

/**
 * Generate unique ID for ARIA relationships
 * @param {string} prefix - Prefix for ID (e.g., 'button')
 * @returns {string} Unique ID
 */
export function generateAriaId(prefix = 'element') {
    return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Check if element is keyboard accessible
 * @param {HTMLElement} element - DOM element to check
 * @returns {boolean} True if keyboard accessible
 */
export function isKeyboardAccessible(element) {
    if (!element) return false;

    // Check if element is natively keyboard accessible
    const nativelyAccessible = ['BUTTON', 'A', 'INPUT', 'SELECT', 'TEXTAREA'].includes(element.tagName);
    const hasTabIndex = element.hasAttribute('tabindex');
    const hasClickHandler = element.onclick !== null || element.hasAttribute('onclick');

    return nativelyAccessible || (hasTabIndex && !element.disabled) || (hasClickHandler && hasTabIndex);
}

/**
 * Get all focusable elements in a container
 * @param {HTMLElement} container - Container to search
 * @returns {HTMLElement[]} Array of focusable elements
 */
export function getFocusableElements(container) {
    if (!container) return [];

    const focusableSelectors = [
        'button',
        'a[href]',
        'input',
        'select',
        'textarea',
        '[tabindex]:not([tabindex="-1"])',
    ].join(',');

    return Array.from(container.querySelectorAll(focusableSelectors))
        .filter(el => !el.disabled && el.offsetParent !== null);
}

/**
 * Check if element is hidden from screen readers
 * @param {HTMLElement} element - DOM element to check
 * @returns {boolean} True if hidden from screen readers
 */
export function isHiddenFromScreenReaders(element) {
    if (!element) return false;

    // Check aria-hidden attribute
    if (element.getAttribute('aria-hidden') === 'true') return true;

    // Check display: none or visibility: hidden
    const style = window.getComputedStyle(element);
    if (style.display === 'none' || style.visibility === 'hidden') return true;

    return false;
}

/**
 * Announce message to screen readers
 * @param {string} message - Message to announce
 * @param {string} priority - 'polite' or 'assertive'
 */
export function announceToScreenReader(message, priority = 'polite') {
    let liveRegion = document.getElementById('a11y-announcements');

    // Create live region if it doesn't exist
    if (!liveRegion) {
        liveRegion = document.createElement('div');
        liveRegion.id = 'a11y-announcements';
        liveRegion.setAttribute('aria-live', priority);
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only'; // Visually hidden
        document.body.appendChild(liveRegion);
    }

    liveRegion.setAttribute('aria-live', priority);
    liveRegion.textContent = message;
}

/**
 * Validate color contrast in a component (development aid)
 * @param {HTMLElement} element - Component element
 * @returns {Array} Array of contrast issues found
 */
export function validateComponentContrast(element) {
    if (!element) return [];

    const issues = [];
    const elements = element.querySelectorAll('*');

    elements.forEach(el => {
        if (isHiddenFromScreenReaders(el)) return;

        const style = window.getComputedStyle(el);
        const bgColor = style.backgroundColor;
        const textColor = style.color;

        // Skip if background or text color is transparent/default
        if (!bgColor || bgColor === 'transparent' || !textColor) return;

        try {
            const ratio = getContrastRatio(textColor, bgColor);
            const isLarge = parseInt(style.fontSize) >= 18 ||
                           (parseInt(style.fontSize) >= 14 && style.fontWeight >= 700);

            if (!meetsWCAGAA(ratio, isLarge)) {
                issues.push({
                    element: el,
                    foreground: textColor,
                    background: bgColor,
                    ratio: ratio.toFixed(2),
                    required: isLarge ? '3:1' : '4.5:1',
                });
            }
        } catch (e) {
            // Ignore conversion errors
        }
    });

    return issues;
}

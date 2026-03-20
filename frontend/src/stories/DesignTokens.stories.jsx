/**
 * Design Tokens — System Documentation
 *
 * Comprehensive visual documentation of the Consulta Processo design system.
 * These tokens are defined in `src/styles/tokens.css` and integrated with
 * Tailwind CSS for consistent styling across all components.
 *
 * Implementation Reference: REM-033 (Design Tokens System)
 * Component Usage Reference: REM-034 (Atomic Component Library)
 */

export default {
  title: 'Design System/Design Tokens',
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'Complete design system token documentation including colors, spacing, typography, and effects.',
      },
    },
  },
};

// ─────────────────────────────────────────
// COLOR PALETTE DOCUMENTATION
// ─────────────────────────────────────────

export const ColorPalette = {
  render: () => (
    <div className="p-8 space-y-12">
      {/* Brand Colors */}
      <section>
        <h2 className="text-2xl font-bold text-text-primary mb-6">Brand Colors</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <ColorSwatch
            name="Brand"
            value="#4f46e5"
            cssVar="--color-brand"
            desc="Primary brand color (indigo-600)"
          />
          <ColorSwatch
            name="Brand Hover"
            value="#4338ca"
            cssVar="--color-brand-hover"
            desc="Brand hover state (indigo-700)"
          />
          <ColorSwatch
            name="Brand Light"
            value="#e0e7ff"
            cssVar="--color-brand-light"
            desc="Brand light background (indigo-100)"
          />
          <ColorSwatch
            name="Brand Foreground"
            value="#ffffff"
            cssVar="--color-brand-fg"
            desc="Text on brand backgrounds"
          />
        </div>
      </section>

      {/* Neutral Palette */}
      <section>
        <h2 className="text-2xl font-bold text-text-primary mb-6">Neutral Palette</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <ColorSwatch
            name="Surface"
            value="#ffffff"
            cssVar="--color-surface"
            desc="Primary background (white)"
          />
          <ColorSwatch
            name="Surface Alt"
            value="#f9fafb"
            cssVar="--color-surface-alt"
            desc="Alternate background (gray-50)"
          />
          <ColorSwatch
            name="Surface Muted"
            value="#f3f4f6"
            cssVar="--color-surface-muted"
            desc="Muted background (gray-100)"
          />
          <ColorSwatch
            name="Border"
            value="#e5e7eb"
            cssVar="--color-border"
            desc="Default border (gray-200)"
          />
        </div>
      </section>

      {/* Text Colors */}
      <section>
        <h2 className="text-2xl font-bold text-text-primary mb-6">Text Colors</h2>
        <p className="text-text-secondary mb-4">
          All text colors meet WCAG AA contrast requirements (minimum 4.5:1 ratio).
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <ColorSwatch
            name="Text Primary"
            value="#111827"
            cssVar="--color-text-primary"
            desc="Main text (gray-900)"
            textClass="text-text-primary"
          />
          <ColorSwatch
            name="Text Secondary"
            value="#374151"
            cssVar="--color-text-secondary"
            desc="Secondary text (gray-700)"
            textClass="text-text-secondary"
          />
          <ColorSwatch
            name="Text Muted"
            value="#4b5563"
            cssVar="--color-text-muted"
            desc="Muted text (gray-600) — 7.0:1"
            textClass="text-text-muted"
          />
          <ColorSwatch
            name="Text Disabled"
            value="#9ca3af"
            cssVar="--color-text-disabled"
            desc="Disabled text (gray-400) — decorative only"
            textClass="text-text-disabled"
          />
        </div>
      </section>

      {/* Semantic Colors */}
      <section>
        <h2 className="text-2xl font-bold text-text-primary mb-6">Semantic Colors</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <ColorSwatch
            name="Success"
            value="#059669"
            cssVar="--color-success"
            desc="Success state (emerald-600)"
          />
          <ColorSwatch
            name="Success BG"
            value="#d1fae5"
            cssVar="--color-success-bg"
            desc="Success background (emerald-100)"
          />
          <ColorSwatch
            name="Error"
            value="#dc2626"
            cssVar="--color-error"
            desc="Error state (red-600)"
          />
          <ColorSwatch
            name="Error BG"
            value="#fee2e2"
            cssVar="--color-error-bg"
            desc="Error background (red-100)"
          />
          <ColorSwatch
            name="Warning"
            value="#d97706"
            cssVar="--color-warning"
            desc="Warning state (amber-600)"
          />
          <ColorSwatch
            name="Warning BG"
            value="#fef3c7"
            cssVar="--color-warning-bg"
            desc="Warning background (amber-100)"
          />
          <ColorSwatch
            name="Info"
            value="#2563eb"
            cssVar="--color-info"
            desc="Info state (blue-600)"
          />
          <ColorSwatch
            name="Info BG"
            value="#dbeafe"
            cssVar="--color-info-bg"
            desc="Info background (blue-100)"
          />
        </div>
      </section>
    </div>
  ),
};

// ─────────────────────────────────────────
// SPACING SCALE
// ─────────────────────────────────────────

export const Spacing = {
  render: () => (
    <div className="p-8 space-y-8">
      <section>
        <h2 className="text-2xl font-bold text-text-primary mb-6">Spacing Scale</h2>
        <p className="text-text-secondary mb-6">
          Consistent spacing scale based on 4px base unit. Used for margins, padding, and gaps.
        </p>
        <div className="space-y-4">
          {[
            { name: '--space-1', value: '0.25rem (4px)', px: 'w-1' },
            { name: '--space-2', value: '0.5rem (8px)', px: 'w-2' },
            { name: '--space-3', value: '0.75rem (12px)', px: 'w-3' },
            { name: '--space-4', value: '1rem (16px)', px: 'w-4' },
            { name: '--space-6', value: '1.5rem (24px)', px: 'w-6' },
            { name: '--space-8', value: '2rem (32px)', px: 'w-8' },
            { name: '--space-12', value: '3rem (48px)', px: 'w-12' },
          ].map(({ name, value, px }) => (
            <div key={name} className="flex items-center gap-4">
              <div className="min-w-32">
                <code className="text-sm font-mono text-primary">{name}</code>
              </div>
              <div className={`${px} bg-primary rounded`} />
              <span className="text-text-secondary text-sm">{value}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  ),
};

// ─────────────────────────────────────────
// TYPOGRAPHY
// ─────────────────────────────────────────

export const Typography = {
  render: () => (
    <div className="p-8 space-y-8">
      <section>
        <h2 className="text-2xl font-bold text-text-primary mb-6">Font Sizes</h2>
        <div className="space-y-4">
          {[
            { name: '--font-size-xs', size: '0.75rem (12px)', className: 'text-xs' },
            { name: '--font-size-sm', size: '0.875rem (14px)', className: 'text-sm' },
            { name: '--font-size-base', size: '1rem (16px)', className: 'text-base' },
            { name: '--font-size-lg', size: '1.125rem (18px)', className: 'text-lg' },
            { name: '--font-size-xl', size: '1.25rem (20px)', className: 'text-xl' },
            { name: '--font-size-2xl', size: '1.5rem (24px)', className: 'text-2xl' },
          ].map(({ name, size, className: cls }) => (
            <div key={name}>
              <code className="text-xs text-primary">{name}</code>
              <p className={`${cls} text-text-primary my-2`}>The quick brown fox jumps over the lazy dog</p>
              <span className="text-xs text-text-secondary">{size}</span>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-bold text-text-primary mb-6">Font Weights</h2>
        <div className="space-y-3">
          {[
            { name: '--font-weight-normal', weight: '400', className: 'font-normal' },
            { name: '--font-weight-medium', weight: '500', className: 'font-medium' },
            { name: '--font-weight-semibold', weight: '600', className: 'font-semibold' },
            { name: '--font-weight-bold', weight: '700', className: 'font-bold' },
            { name: '--font-weight-extrabold', weight: '800', className: 'font-extrabold' },
          ].map(({ name, weight, className: cls }) => (
            <div key={name}>
              <p className={`${cls} text-base text-text-primary`}>The quick brown fox jumps</p>
              <code className="text-xs text-primary">{name}: {weight}</code>
            </div>
          ))}
        </div>
      </section>
    </div>
  ),
};

// ─────────────────────────────────────────
// SHADOWS & BORDER RADIUS
// ─────────────────────────────────────────

export const Effects = {
  render: () => (
    <div className="p-8 space-y-12">
      <section>
        <h2 className="text-2xl font-bold text-text-primary mb-6">Shadows</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 bg-surface rounded-lg shadow-sm border border-border">
            <p className="text-sm text-text-secondary mb-2">Small Shadow</p>
            <p className="font-mono text-xs text-primary">--shadow-sm</p>
          </div>
          <div className="p-6 bg-surface rounded-lg shadow-md border border-border">
            <p className="text-sm text-text-secondary mb-2">Medium Shadow</p>
            <p className="font-mono text-xs text-primary">--shadow-md</p>
          </div>
          <div className="p-6 bg-surface rounded-lg shadow-lg border border-border">
            <p className="text-sm text-text-secondary mb-2">Large Shadow</p>
            <p className="font-mono text-xs text-primary">--shadow-lg</p>
          </div>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-bold text-text-primary mb-6">Border Radius</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[
            { name: '--radius-sm', class: 'rounded-sm' },
            { name: '--radius-md', class: 'rounded-md' },
            { name: '--radius-lg', class: 'rounded-lg' },
            { name: '--radius-xl', class: 'rounded-xl' },
            { name: '--radius-full', class: 'rounded-full' },
          ].map(({ name, class: cls }) => (
            <div key={name}>
              <div className={`${cls} w-20 h-20 bg-primary mb-2`} />
              <code className="text-xs text-primary block">{name}</code>
            </div>
          ))}
        </div>
      </section>
    </div>
  ),
};

// ─────────────────────────────────────────
// COMPONENT: ColorSwatch
// ─────────────────────────────────────────

function ColorSwatch({ name, value, cssVar, desc, textClass }) {
  return (
    <div className="space-y-2">
      <div
        className="w-full h-24 rounded-lg border-2 border-border shadow-sm"
        style={{ backgroundColor: value }}
      />
      <div>
        <h4 className={`font-semibold text-sm ${textClass || 'text-text-primary'}`}>
          {name}
        </h4>
        <code className="text-xs text-primary block">{cssVar}</code>
        <code className="text-xs text-text-secondary block">{value}</code>
        <p className="text-xs text-text-secondary mt-1">{desc}</p>
      </div>
    </div>
  );
}

import { Input } from '../components/ui/input';

/**
 * Input Component — Atomic Design System
 *
 * Accessible text input field with support for various states and types.
 *
 * **Features:**
 * - Full keyboard navigation support
 * - Focus indicators (focus-visible ring)
 * - Disabled state with reduced opacity
 * - Placeholder text styling
 * - Support for all standard input types
 * - Dark mode support
 * - WCAG AA compliant
 *
 * **Input Types Supported:**
 * - text (default)
 * - email
 * - password
 * - number
 * - search
 * - tel
 * - url
 * - date
 * - time
 * - checkbox
 * - radio
 */

export default {
  title: 'Components/Input',
  component: Input,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    type: {
      control: 'select',
      options: ['text', 'email', 'password', 'number', 'search', 'tel', 'url', 'date', 'time'],
      description: 'HTML input type',
    },
    placeholder: {
      control: 'text',
      description: 'Placeholder text',
    },
    disabled: {
      control: 'boolean',
      description: 'Disable input interactions',
    },
  },
};

// ─────────────────────────────────────────
// TEXT INPUT
// ─────────────────────────────────────────

export const Text = {
  args: {
    type: 'text',
    placeholder: 'Enter text...',
  },
};

// ─────────────────────────────────────────
// EMAIL INPUT
// ─────────────────────────────────────────

export const Email = {
  args: {
    type: 'email',
    placeholder: 'your@email.com',
  },
};

// ─────────────────────────────────────────
// PASSWORD INPUT
// ─────────────────────────────────────────

export const Password = {
  args: {
    type: 'password',
    placeholder: 'Enter password...',
  },
};

// ─────────────────────────────────────────
// NUMBER INPUT
// ─────────────────────────────────────────

export const Number = {
  args: {
    type: 'number',
    placeholder: 'Enter a number...',
  },
};

// ─────────────────────────────────────────
// SEARCH INPUT
// ─────────────────────────────────────────

export const Search = {
  args: {
    type: 'search',
    placeholder: 'Search...',
  },
};

// ─────────────────────────────────────────
// TELEPHONE INPUT
// ─────────────────────────────────────────

export const Telephone = {
  args: {
    type: 'tel',
    placeholder: '(123) 456-7890',
  },
};

// ─────────────────────────────────────────
// URL INPUT
// ─────────────────────────────────────────

export const URL = {
  args: {
    type: 'url',
    placeholder: 'https://example.com',
  },
};

// ─────────────────────────────────────────
// DATE INPUT
// ─────────────────────────────────────────

export const Date = {
  args: {
    type: 'date',
  },
};

// ─────────────────────────────────────────
// TIME INPUT
// ─────────────────────────────────────────

export const Time = {
  args: {
    type: 'time',
  },
};

// ─────────────────────────────────────────
// DISABLED STATE
// ─────────────────────────────────────────

export const Disabled = {
  args: {
    type: 'text',
    placeholder: 'This input is disabled',
    disabled: true,
  },
};

// ─────────────────────────────────────────
// WITH VALUE
// ─────────────────────────────────────────

export const WithValue = {
  args: {
    type: 'text',
    placeholder: 'Placeholder text',
    defaultValue: 'Pre-filled value',
  },
};

// ─────────────────────────────────────────
// FORM GROUP
// ─────────────────────────────────────────

export const FormGroup = {
  render: () => (
    <form className="w-full max-w-md space-y-4">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-text-primary mb-2">
          Full Name
        </label>
        <Input
          id="name"
          type="text"
          placeholder="John Doe"
        />
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-text-primary mb-2">
          Email Address
        </label>
        <Input
          id="email"
          type="email"
          placeholder="john@example.com"
        />
      </div>

      <div>
        <label htmlFor="phone" className="block text-sm font-medium text-text-primary mb-2">
          Phone Number
        </label>
        <Input
          id="phone"
          type="tel"
          placeholder="(123) 456-7890"
        />
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-text-primary mb-2">
          Password
        </label>
        <Input
          id="password"
          type="password"
          placeholder="••••••••"
        />
      </div>
    </form>
  ),
};

// ─────────────────────────────────────────
// SEARCH FORM
// ─────────────────────────────────────────

export const SearchForm = {
  render: () => (
    <div className="w-full max-w-md">
      <label htmlFor="search" className="block text-sm font-medium text-text-primary mb-2">
        Search
      </label>
      <div className="relative">
        <Input
          id="search"
          type="search"
          placeholder="Search processes, cases..."
          className="pl-10"
        />
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted">🔍</span>
      </div>
    </div>
  ),
};

// ─────────────────────────────────────────
// VALIDATION STATES
// ─────────────────────────────────────────

export const ValidationStates = {
  render: () => (
    <div className="w-full max-w-md space-y-4">
      <div>
        <label htmlFor="valid" className="block text-sm font-medium text-text-primary mb-2">
          Valid Input
        </label>
        <Input
          id="valid"
          type="text"
          defaultValue="john@example.com"
          className="border-success"
        />
        <p className="text-xs text-success mt-1">✓ Input is valid</p>
      </div>

      <div>
        <label htmlFor="invalid" className="block text-sm font-medium text-text-primary mb-2">
          Invalid Input
        </label>
        <Input
          id="invalid"
          type="email"
          defaultValue="not-an-email"
          className="border-error"
        />
        <p className="text-xs text-error mt-1">✕ Please enter a valid email</p>
      </div>

      <div>
        <label htmlFor="warning" className="block text-sm font-medium text-text-primary mb-2">
          Warning Input
        </label>
        <Input
          id="warning"
          type="text"
          defaultValue="Some value"
          className="border-warning"
        />
        <p className="text-xs text-warning mt-1">⚠ This field needs review</p>
      </div>
    </div>
  ),
};

// ─────────────────────────────────────────
// ALL TYPES
// ─────────────────────────────────────────

export const AllTypes = {
  render: () => (
    <div className="w-full max-w-md space-y-4">
      {[
        { type: 'text', label: 'Text', placeholder: 'Text input' },
        { type: 'email', label: 'Email', placeholder: 'email@example.com' },
        { type: 'password', label: 'Password', placeholder: '••••••••' },
        { type: 'number', label: 'Number', placeholder: '0' },
        { type: 'search', label: 'Search', placeholder: 'Search...' },
        { type: 'tel', label: 'Telephone', placeholder: '(123) 456-7890' },
        { type: 'url', label: 'URL', placeholder: 'https://example.com' },
        { type: 'date', label: 'Date' },
        { type: 'time', label: 'Time' },
      ].map(({ type, label, placeholder }) => (
        <div key={type}>
          <label className="block text-sm font-medium text-text-primary mb-2">
            {label}
          </label>
          <Input
            type={type}
            placeholder={placeholder}
          />
        </div>
      ))}
    </div>
  ),
};

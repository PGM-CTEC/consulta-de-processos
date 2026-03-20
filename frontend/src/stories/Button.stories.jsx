import { Button } from '../components/ui/button';

/**
 * Button Component — Atomic Design System
 *
 * Core interactive element with 6 variants and 3 sizes.
 * Includes focus management, disabled states, and full WCAG AA compliance.
 *
 * **Variants:**
 * - default: Primary brand color with hover effect
 * - secondary: Secondary color with 80% hover opacity
 * - ghost: Subtle, accent-only on hover
 * - link: Text button with underline
 * - destructive: Red color for destructive actions
 * - outline: Border-only button
 *
 * **Sizes:**
 * - sm: Small (h-9, px-3)
 * - default/md: Standard (h-10, px-4)
 * - lg: Large (h-11, px-8)
 * - icon: Square (h-10, w-10)
 */

export default {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    a11y: {
      config: {
        rules: [
          {
            id: 'color-contrast',
            enabled: true,
          },
        ],
      },
    },
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'secondary', 'ghost', 'link', 'destructive', 'outline'],
      description: 'Button style variant',
    },
    size: {
      control: 'select',
      options: ['sm', 'default', 'lg', 'icon'],
      description: 'Button size',
    },
    disabled: {
      control: 'boolean',
      description: 'Disable button interactions',
    },
    children: {
      control: 'text',
      description: 'Button label text',
    },
  },
};

// ─────────────────────────────────────────
// DEFAULT VARIANT
// ─────────────────────────────────────────

export const Default = {
  args: {
    children: 'Click Me',
    variant: 'default',
    size: 'default',
  },
};

export const DefaultSmall = {
  args: {
    children: 'Small',
    variant: 'default',
    size: 'sm',
  },
};

export const DefaultLarge = {
  args: {
    children: 'Large',
    variant: 'default',
    size: 'lg',
  },
};

export const DefaultIcon = {
  args: {
    children: '✓',
    variant: 'default',
    size: 'icon',
  },
};

// ─────────────────────────────────────────
// SECONDARY VARIANT
// ─────────────────────────────────────────

export const Secondary = {
  args: {
    children: 'Secondary',
    variant: 'secondary',
    size: 'default',
  },
};

export const SecondarySmall = {
  args: {
    children: 'Small',
    variant: 'secondary',
    size: 'sm',
  },
};

export const SecondaryLarge = {
  args: {
    children: 'Large',
    variant: 'secondary',
    size: 'lg',
  },
};

// ─────────────────────────────────────────
// GHOST VARIANT
// ─────────────────────────────────────────

export const Ghost = {
  args: {
    children: 'Ghost',
    variant: 'ghost',
    size: 'default',
  },
};

export const GhostSmall = {
  args: {
    children: 'Small',
    variant: 'ghost',
    size: 'sm',
  },
};

export const GhostLarge = {
  args: {
    children: 'Large',
    variant: 'ghost',
    size: 'lg',
  },
};

// ─────────────────────────────────────────
// LINK VARIANT
// ─────────────────────────────────────────

export const Link = {
  args: {
    children: 'Link Button',
    variant: 'link',
    size: 'default',
  },
};

export const LinkSmall = {
  args: {
    children: 'Small',
    variant: 'link',
    size: 'sm',
  },
};

export const LinkLarge = {
  args: {
    children: 'Large',
    variant: 'link',
    size: 'lg',
  },
};

// ─────────────────────────────────────────
// DESTRUCTIVE VARIANT
// ─────────────────────────────────────────

export const Destructive = {
  args: {
    children: 'Delete',
    variant: 'destructive',
    size: 'default',
  },
};

export const DestructiveSmall = {
  args: {
    children: 'Delete',
    variant: 'destructive',
    size: 'sm',
  },
};

export const DestructiveLarge = {
  args: {
    children: 'Delete',
    variant: 'destructive',
    size: 'lg',
  },
};

// ─────────────────────────────────────────
// OUTLINE VARIANT
// ─────────────────────────────────────────

export const Outline = {
  args: {
    children: 'Outline',
    variant: 'outline',
    size: 'default',
  },
};

export const OutlineSmall = {
  args: {
    children: 'Small',
    variant: 'outline',
    size: 'sm',
  },
};

export const OutlineLarge = {
  args: {
    children: 'Large',
    variant: 'outline',
    size: 'lg',
  },
};

// ─────────────────────────────────────────
// DISABLED STATES
// ─────────────────────────────────────────

export const Disabled = {
  args: {
    children: 'Disabled',
    variant: 'default',
    size: 'default',
    disabled: true,
  },
};

export const DisabledSecondary = {
  args: {
    children: 'Disabled',
    variant: 'secondary',
    size: 'default',
    disabled: true,
  },
};

export const DisabledDestructive = {
  args: {
    children: 'Delete',
    variant: 'destructive',
    size: 'default',
    disabled: true,
  },
};

// ─────────────────────────────────────────
// GROUPED BUTTONS
// ─────────────────────────────────────────

export const ButtonGroup = {
  render: () => (
    <div className="flex gap-2">
      <Button variant="default">Save</Button>
      <Button variant="secondary">Cancel</Button>
      <Button variant="destructive">Delete</Button>
    </div>
  ),
};

export const AllSizes = {
  render: () => (
    <div className="flex gap-2 items-center">
      <Button size="sm">Small</Button>
      <Button size="default">Default</Button>
      <Button size="lg">Large</Button>
      <Button size="icon">✓</Button>
    </div>
  ),
};

export const AllVariants = {
  render: () => (
    <div className="flex flex-col gap-3">
      <Button variant="default">Default</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="link">Link</Button>
      <Button variant="destructive">Destructive</Button>
      <Button variant="outline">Outline</Button>
    </div>
  ),
};

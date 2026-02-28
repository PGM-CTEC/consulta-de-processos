import { Badge } from '../components/ui/badge';

/**
 * Badge Component — Atomic Design System
 *
 * Small inline labels with 4 semantic variants.
 *
 * **Variants:**
 * - default: Primary brand color
 * - secondary: Secondary color
 * - destructive: Red for error/delete states
 * - outline: Border-only variant
 *
 * **Use Cases:**
 * - Status indicators (active, pending, completed)
 * - Category tags
 * - Priority levels
 * - Count badges
 */

export default {
  title: 'Components/Badge',
  component: Badge,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'secondary', 'destructive', 'outline'],
      description: 'Badge color variant',
    },
    children: {
      control: 'text',
      description: 'Badge label text',
    },
  },
};

// ─────────────────────────────────────────
// DEFAULT VARIANT
// ─────────────────────────────────────────

export const Default = {
  args: {
    children: 'Badge',
    variant: 'default',
  },
};

// ─────────────────────────────────────────
// SECONDARY VARIANT
// ─────────────────────────────────────────

export const Secondary = {
  args: {
    children: 'Secondary',
    variant: 'secondary',
  },
};

// ─────────────────────────────────────────
// DESTRUCTIVE VARIANT
// ─────────────────────────────────────────

export const Destructive = {
  args: {
    children: 'Destructive',
    variant: 'destructive',
  },
};

// ─────────────────────────────────────────
// OUTLINE VARIANT
// ─────────────────────────────────────────

export const Outline = {
  args: {
    children: 'Outline',
    variant: 'outline',
  },
};

// ─────────────────────────────────────────
// STATUS BADGES
// ─────────────────────────────────────────

export const StatusBadges = {
  render: () => (
    <div className="flex gap-2">
      <Badge variant="default">✓ Active</Badge>
      <Badge variant="secondary">⏱ Pending</Badge>
      <Badge variant="destructive">✕ Inactive</Badge>
      <Badge variant="outline">? Unknown</Badge>
    </div>
  ),
};

// ─────────────────────────────────────────
// PRIORITY BADGES
// ─────────────────────────────────────────

export const PriorityBadges = {
  render: () => (
    <div className="flex gap-2">
      <Badge variant="destructive">🔴 Critical</Badge>
      <Badge variant="default">🟠 High</Badge>
      <Badge variant="secondary">🟡 Medium</Badge>
      <Badge variant="outline">🟢 Low</Badge>
    </div>
  ),
};

// ─────────────────────────────────────────
// CATEGORY TAGS
// ─────────────────────────────────────────

export const CategoryTags = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Badge variant="default">Design</Badge>
      <Badge variant="secondary">Frontend</Badge>
      <Badge variant="default">React</Badge>
      <Badge variant="secondary">Accessibility</Badge>
      <Badge variant="default">Components</Badge>
      <Badge variant="secondary">UI</Badge>
    </div>
  ),
};

// ─────────────────────────────────────────
// WITH COUNTS
// ─────────────────────────────────────────

export const WithCounts = {
  render: () => (
    <div className="flex gap-2">
      <Badge variant="default">Comments (5)</Badge>
      <Badge variant="secondary">Tasks (12)</Badge>
      <Badge variant="destructive">Errors (2)</Badge>
      <Badge variant="outline">Warnings (8)</Badge>
    </div>
  ),
};

// ─────────────────────────────────────────
// IN CONTEXT
// ─────────────────────────────────────────

export const InContext = {
  render: () => (
    <div className="space-y-4 max-w-md">
      <div className="p-4 border rounded-lg">
        <div className="flex items-center gap-2 mb-2">
          <h3 className="font-semibold">Task Title</h3>
          <Badge variant="default">New</Badge>
        </div>
        <p className="text-sm text-text-secondary mb-3">
          Description of the task that needs to be completed.
        </p>
        <div className="flex gap-2">
          <Badge variant="secondary">Design</Badge>
          <Badge variant="secondary">In Progress</Badge>
        </div>
      </div>

      <div className="p-4 border rounded-lg">
        <div className="flex items-center gap-2 mb-2">
          <h3 className="font-semibold">Bug Report</h3>
          <Badge variant="destructive">Critical</Badge>
        </div>
        <p className="text-sm text-text-secondary mb-3">
          Critical issue affecting production functionality.
        </p>
        <div className="flex gap-2">
          <Badge variant="destructive">Bug</Badge>
          <Badge variant="destructive">Unassigned</Badge>
        </div>
      </div>
    </div>
  ),
};

// ─────────────────────────────────────────
// ALL VARIANTS
// ─────────────────────────────────────────

export const AllVariants = {
  render: () => (
    <div className="flex flex-col gap-4">
      <div>
        <p className="text-sm font-semibold text-text-secondary mb-2">Default</p>
        <Badge variant="default">Default Badge</Badge>
      </div>
      <div>
        <p className="text-sm font-semibold text-text-secondary mb-2">Secondary</p>
        <Badge variant="secondary">Secondary Badge</Badge>
      </div>
      <div>
        <p className="text-sm font-semibold text-text-secondary mb-2">Destructive</p>
        <Badge variant="destructive">Destructive Badge</Badge>
      </div>
      <div>
        <p className="text-sm font-semibold text-text-secondary mb-2">Outline</p>
        <Badge variant="outline">Outline Badge</Badge>
      </div>
    </div>
  ),
};

import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from '../components/ui/card';
import { Button } from '../components/ui/button';

/**
 * Card Component — Atomic Design System
 *
 * Composable card container with semantic sections:
 * - Card: Root container with border, shadow, and rounded corners
 * - CardHeader: Top section with spacing
 * - CardTitle: Header text with typography
 * - CardContent: Main content area
 * - CardFooter: Bottom action area with flex layout
 *
 * **Features:**
 * - Responsive shadow and rounded corners
 * - Flexbox footer for button alignment
 * - Semantic HTML structure
 * - Tailwind CSS design tokens integration
 */

export default {
  title: 'Components/Card',
  component: Card,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
};

// ─────────────────────────────────────────
// BASIC CARD
// ─────────────────────────────────────────

export const BasicCard = {
  render: () => (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Basic Card</CardTitle>
      </CardHeader>
      <CardContent>
        <p>This is a simple card with header and content.</p>
      </CardContent>
    </Card>
  ),
};

// ─────────────────────────────────────────
// CARD WITH ACTIONS
// ─────────────────────────────────────────

export const CardWithActions = {
  render: () => (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Card with Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <p>This card includes action buttons in the footer section.</p>
      </CardContent>
      <CardFooter className="flex gap-2">
        <Button variant="secondary">Cancel</Button>
        <Button>Save</Button>
      </CardFooter>
    </Card>
  ),
};

// ─────────────────────────────────────────
// FULL FEATURED CARD
// ─────────────────────────────────────────

export const FullFeaturedCard = {
  render: () => (
    <Card className="w-[400px]">
      <CardHeader>
        <CardTitle>Full Featured Card</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="font-semibold mb-2">Features</h4>
          <ul className="list-disc list-inside text-sm text-text-secondary">
            <li>Semantic HTML structure</li>
            <li>Responsive design</li>
            <li>Dark mode support</li>
            <li>Accessibility focused</li>
          </ul>
        </div>
      </CardContent>
      <CardFooter className="flex gap-2 justify-end">
        <Button variant="outline">Learn More</Button>
        <Button>Get Started</Button>
      </CardFooter>
    </Card>
  ),
};

// ─────────────────────────────────────────
// COMPACT CARD
// ─────────────────────────────────────────

export const CompactCard = {
  render: () => (
    <Card className="w-[300px]">
      <CardContent className="pt-6">
        <div className="text-center">
          <div className="text-3xl font-bold text-primary">42</div>
          <p className="text-sm text-text-secondary mt-2">Total Items</p>
        </div>
      </CardContent>
    </Card>
  ),
};

// ─────────────────────────────────────────
// CARD GRID
// ─────────────────────────────────────────

export const CardGrid = {
  render: () => (
    <div className="grid grid-cols-3 gap-4 w-full max-w-4xl">
      {[1, 2, 3, 4, 5, 6].map((num) => (
        <Card key={num} className="h-full">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">Card {num}</div>
              <p className="text-xs text-text-secondary mt-2">Sample card</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  ),
};

// ─────────────────────────────────────────
// CARD WITH IMAGE
// ─────────────────────────────────────────

export const CardWithImage = {
  render: () => (
    <Card className="w-[350px] overflow-hidden">
      <div className="h-48 bg-gradient-to-br from-primary to-secondary" />
      <CardHeader>
        <CardTitle>Image Card</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-text-secondary">
          Cards can include images or hero sections at the top.
        </p>
      </CardContent>
    </Card>
  ),
};

// ─────────────────────────────────────────
// FORM CARD
// ─────────────────────────────────────────

export const FormCard = {
  render: () => (
    <Card className="w-[400px]">
      <CardHeader>
        <CardTitle>Sign In</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium mb-1">
            Email
          </label>
          <input
            id="email"
            type="email"
            placeholder="your@email.com"
            className="w-full px-3 py-2 border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm font-medium mb-1">
            Password
          </label>
          <input
            id="password"
            type="password"
            placeholder="••••••••"
            className="w-full px-3 py-2 border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
      </CardContent>
      <CardFooter>
        <Button className="w-full">Sign In</Button>
      </CardFooter>
    </Card>
  ),
};

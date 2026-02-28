import{j as e}from"./jsx-runtime-u17CrQMm.js";import{B as r}from"./button-D3x7JmdK.js";import"./index-LHNt3CwB.js";import"./utils-BQHNewu7.js";const C={title:"Components/Button",component:r,tags:["autodocs"],parameters:{layout:"centered",a11y:{config:{rules:[{id:"color-contrast",enabled:!0}]}},docs:{description:{component:`Button Component — Atomic Design System\r

Core interactive element with 6 variants and 3 sizes.\r
Includes focus management, disabled states, and full WCAG AA compliance.\r

**Variants:**\r
- default: Primary brand color with hover effect\r
- secondary: Secondary color with 80% hover opacity\r
- ghost: Subtle, accent-only on hover\r
- link: Text button with underline\r
- destructive: Red color for destructive actions\r
- outline: Border-only button\r

**Sizes:**\r
- sm: Small (h-9, px-3)\r
- default/md: Standard (h-10, px-4)\r
- lg: Large (h-11, px-8)\r
- icon: Square (h-10, w-10)`}}},argTypes:{variant:{control:"select",options:["default","secondary","ghost","link","destructive","outline"],description:"Button style variant"},size:{control:"select",options:["sm","default","lg","icon"],description:"Button size"},disabled:{control:"boolean",description:"Disable button interactions"},children:{control:"text",description:"Button label text"}}},a={args:{children:"Click Me",variant:"default",size:"default"}},n={args:{children:"Small",variant:"default",size:"sm"}},s={args:{children:"Large",variant:"default",size:"lg"}},t={args:{children:"✓",variant:"default",size:"icon"}},o={args:{children:"Secondary",variant:"secondary",size:"default"}},i={args:{children:"Small",variant:"secondary",size:"sm"}},c={args:{children:"Large",variant:"secondary",size:"lg"}},l={args:{children:"Ghost",variant:"ghost",size:"default"}},d={args:{children:"Small",variant:"ghost",size:"sm"}},u={args:{children:"Large",variant:"ghost",size:"lg"}},m={args:{children:"Link Button",variant:"link",size:"default"}},p={args:{children:"Small",variant:"link",size:"sm"}},g={args:{children:"Large",variant:"link",size:"lg"}},v={args:{children:"Delete",variant:"destructive",size:"default"}},h={args:{children:"Delete",variant:"destructive",size:"sm"}},S={args:{children:"Delete",variant:"destructive",size:"lg"}},f={args:{children:"Outline",variant:"outline",size:"default"}},z={args:{children:"Small",variant:"outline",size:"sm"}},D={args:{children:"Large",variant:"outline",size:"lg"}},B={args:{children:"Disabled",variant:"default",size:"default",disabled:!0}},y={args:{children:"Disabled",variant:"secondary",size:"default",disabled:!0}},L={args:{children:"Delete",variant:"destructive",size:"default",disabled:!0}},x={render:()=>e.jsxs("div",{className:"flex gap-2",children:[e.jsx(r,{variant:"default",children:"Save"}),e.jsx(r,{variant:"secondary",children:"Cancel"}),e.jsx(r,{variant:"destructive",children:"Delete"})]})},b={render:()=>e.jsxs("div",{className:"flex gap-2 items-center",children:[e.jsx(r,{size:"sm",children:"Small"}),e.jsx(r,{size:"default",children:"Default"}),e.jsx(r,{size:"lg",children:"Large"}),e.jsx(r,{size:"icon",children:"✓"})]})},k={render:()=>e.jsxs("div",{className:"flex flex-col gap-3",children:[e.jsx(r,{variant:"default",children:"Default"}),e.jsx(r,{variant:"secondary",children:"Secondary"}),e.jsx(r,{variant:"ghost",children:"Ghost"}),e.jsx(r,{variant:"link",children:"Link"}),e.jsx(r,{variant:"destructive",children:"Destructive"}),e.jsx(r,{variant:"outline",children:"Outline"})]})};a.parameters={...a.parameters,docs:{...a.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Click Me',
    variant: 'default',
    size: 'default'
  }
}`,...a.parameters?.docs?.source}}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Small',
    variant: 'default',
    size: 'sm'
  }
}`,...n.parameters?.docs?.source}}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Large',
    variant: 'default',
    size: 'lg'
  }
}`,...s.parameters?.docs?.source}}};t.parameters={...t.parameters,docs:{...t.parameters?.docs,source:{originalSource:`{
  args: {
    children: '✓',
    variant: 'default',
    size: 'icon'
  }
}`,...t.parameters?.docs?.source}}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Secondary',
    variant: 'secondary',
    size: 'default'
  }
}`,...o.parameters?.docs?.source}}};i.parameters={...i.parameters,docs:{...i.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Small',
    variant: 'secondary',
    size: 'sm'
  }
}`,...i.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Large',
    variant: 'secondary',
    size: 'lg'
  }
}`,...c.parameters?.docs?.source}}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Ghost',
    variant: 'ghost',
    size: 'default'
  }
}`,...l.parameters?.docs?.source}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Small',
    variant: 'ghost',
    size: 'sm'
  }
}`,...d.parameters?.docs?.source}}};u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Large',
    variant: 'ghost',
    size: 'lg'
  }
}`,...u.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Link Button',
    variant: 'link',
    size: 'default'
  }
}`,...m.parameters?.docs?.source}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Small',
    variant: 'link',
    size: 'sm'
  }
}`,...p.parameters?.docs?.source}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Large',
    variant: 'link',
    size: 'lg'
  }
}`,...g.parameters?.docs?.source}}};v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Delete',
    variant: 'destructive',
    size: 'default'
  }
}`,...v.parameters?.docs?.source}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Delete',
    variant: 'destructive',
    size: 'sm'
  }
}`,...h.parameters?.docs?.source}}};S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Delete',
    variant: 'destructive',
    size: 'lg'
  }
}`,...S.parameters?.docs?.source}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Outline',
    variant: 'outline',
    size: 'default'
  }
}`,...f.parameters?.docs?.source}}};z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Small',
    variant: 'outline',
    size: 'sm'
  }
}`,...z.parameters?.docs?.source}}};D.parameters={...D.parameters,docs:{...D.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Large',
    variant: 'outline',
    size: 'lg'
  }
}`,...D.parameters?.docs?.source}}};B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Disabled',
    variant: 'default',
    size: 'default',
    disabled: true
  }
}`,...B.parameters?.docs?.source}}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Disabled',
    variant: 'secondary',
    size: 'default',
    disabled: true
  }
}`,...y.parameters?.docs?.source}}};L.parameters={...L.parameters,docs:{...L.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Delete',
    variant: 'destructive',
    size: 'default',
    disabled: true
  }
}`,...L.parameters?.docs?.source}}};x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  render: () => <div className="flex gap-2">\r
      <Button variant="default">Save</Button>\r
      <Button variant="secondary">Cancel</Button>\r
      <Button variant="destructive">Delete</Button>\r
    </div>
}`,...x.parameters?.docs?.source}}};b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  render: () => <div className="flex gap-2 items-center">\r
      <Button size="sm">Small</Button>\r
      <Button size="default">Default</Button>\r
      <Button size="lg">Large</Button>\r
      <Button size="icon">✓</Button>\r
    </div>
}`,...b.parameters?.docs?.source}}};k.parameters={...k.parameters,docs:{...k.parameters?.docs,source:{originalSource:`{
  render: () => <div className="flex flex-col gap-3">\r
      <Button variant="default">Default</Button>\r
      <Button variant="secondary">Secondary</Button>\r
      <Button variant="ghost">Ghost</Button>\r
      <Button variant="link">Link</Button>\r
      <Button variant="destructive">Destructive</Button>\r
      <Button variant="outline">Outline</Button>\r
    </div>
}`,...k.parameters?.docs?.source}}};const N=["Default","DefaultSmall","DefaultLarge","DefaultIcon","Secondary","SecondarySmall","SecondaryLarge","Ghost","GhostSmall","GhostLarge","Link","LinkSmall","LinkLarge","Destructive","DestructiveSmall","DestructiveLarge","Outline","OutlineSmall","OutlineLarge","Disabled","DisabledSecondary","DisabledDestructive","ButtonGroup","AllSizes","AllVariants"];export{b as AllSizes,k as AllVariants,x as ButtonGroup,a as Default,t as DefaultIcon,s as DefaultLarge,n as DefaultSmall,v as Destructive,S as DestructiveLarge,h as DestructiveSmall,B as Disabled,L as DisabledDestructive,y as DisabledSecondary,l as Ghost,u as GhostLarge,d as GhostSmall,m as Link,g as LinkLarge,p as LinkSmall,f as Outline,D as OutlineLarge,z as OutlineSmall,o as Secondary,c as SecondaryLarge,i as SecondarySmall,N as __namedExportsOrder,C as default};

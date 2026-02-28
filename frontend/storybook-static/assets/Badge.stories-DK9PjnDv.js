import{j as e}from"./jsx-runtime-u17CrQMm.js";import{c as x}from"./index-LHNt3CwB.js";import{c as p}from"./utils-BQHNewu7.js";const f=x("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",{variants:{variant:{default:"border-transparent bg-primary text-primary-foreground",secondary:"border-transparent bg-secondary text-secondary-foreground",destructive:"border-transparent bg-destructive text-destructive-foreground",outline:"text-foreground"}},defaultVariants:{variant:"default"}});function a({className:g,variant:v,...u}){return e.jsx("div",{className:p(f({variant:v}),g),...u})}a.__docgenInfo={description:"",methods:[],displayName:"Badge"};const j={title:"Components/Badge",component:a,tags:["autodocs"],parameters:{layout:"centered",docs:{description:{component:`Badge Component — Atomic Design System\r

Small inline labels with 4 semantic variants.\r

**Variants:**\r
- default: Primary brand color\r
- secondary: Secondary color\r
- destructive: Red for error/delete states\r
- outline: Border-only variant\r

**Use Cases:**\r
- Status indicators (active, pending, completed)\r
- Category tags\r
- Priority levels\r
- Count badges`}}},argTypes:{variant:{control:"select",options:["default","secondary","destructive","outline"],description:"Badge color variant"},children:{control:"text",description:"Badge label text"}}},r={args:{children:"Badge",variant:"default"}},n={args:{children:"Secondary",variant:"secondary"}},s={args:{children:"Destructive",variant:"destructive"}},t={args:{children:"Outline",variant:"outline"}},d={render:()=>e.jsxs("div",{className:"flex gap-2",children:[e.jsx(a,{variant:"default",children:"✓ Active"}),e.jsx(a,{variant:"secondary",children:"⏱ Pending"}),e.jsx(a,{variant:"destructive",children:"✕ Inactive"}),e.jsx(a,{variant:"outline",children:"? Unknown"})]})},i={render:()=>e.jsxs("div",{className:"flex gap-2",children:[e.jsx(a,{variant:"destructive",children:"🔴 Critical"}),e.jsx(a,{variant:"default",children:"🟠 High"}),e.jsx(a,{variant:"secondary",children:"🟡 Medium"}),e.jsx(a,{variant:"outline",children:"🟢 Low"})]})},c={render:()=>e.jsxs("div",{className:"flex flex-wrap gap-2",children:[e.jsx(a,{variant:"default",children:"Design"}),e.jsx(a,{variant:"secondary",children:"Frontend"}),e.jsx(a,{variant:"default",children:"React"}),e.jsx(a,{variant:"secondary",children:"Accessibility"}),e.jsx(a,{variant:"default",children:"Components"}),e.jsx(a,{variant:"secondary",children:"UI"})]})},o={render:()=>e.jsxs("div",{className:"flex gap-2",children:[e.jsx(a,{variant:"default",children:"Comments (5)"}),e.jsx(a,{variant:"secondary",children:"Tasks (12)"}),e.jsx(a,{variant:"destructive",children:"Errors (2)"}),e.jsx(a,{variant:"outline",children:"Warnings (8)"})]})},l={render:()=>e.jsxs("div",{className:"space-y-4 max-w-md",children:[e.jsxs("div",{className:"p-4 border rounded-lg",children:[e.jsxs("div",{className:"flex items-center gap-2 mb-2",children:[e.jsx("h3",{className:"font-semibold",children:"Task Title"}),e.jsx(a,{variant:"default",children:"New"})]}),e.jsx("p",{className:"text-sm text-text-secondary mb-3",children:"Description of the task that needs to be completed."}),e.jsxs("div",{className:"flex gap-2",children:[e.jsx(a,{variant:"secondary",children:"Design"}),e.jsx(a,{variant:"secondary",children:"In Progress"})]})]}),e.jsxs("div",{className:"p-4 border rounded-lg",children:[e.jsxs("div",{className:"flex items-center gap-2 mb-2",children:[e.jsx("h3",{className:"font-semibold",children:"Bug Report"}),e.jsx(a,{variant:"destructive",children:"Critical"})]}),e.jsx("p",{className:"text-sm text-text-secondary mb-3",children:"Critical issue affecting production functionality."}),e.jsxs("div",{className:"flex gap-2",children:[e.jsx(a,{variant:"destructive",children:"Bug"}),e.jsx(a,{variant:"destructive",children:"Unassigned"})]})]})]})},m={render:()=>e.jsxs("div",{className:"flex flex-col gap-4",children:[e.jsxs("div",{children:[e.jsx("p",{className:"text-sm font-semibold text-text-secondary mb-2",children:"Default"}),e.jsx(a,{variant:"default",children:"Default Badge"})]}),e.jsxs("div",{children:[e.jsx("p",{className:"text-sm font-semibold text-text-secondary mb-2",children:"Secondary"}),e.jsx(a,{variant:"secondary",children:"Secondary Badge"})]}),e.jsxs("div",{children:[e.jsx("p",{className:"text-sm font-semibold text-text-secondary mb-2",children:"Destructive"}),e.jsx(a,{variant:"destructive",children:"Destructive Badge"})]}),e.jsxs("div",{children:[e.jsx("p",{className:"text-sm font-semibold text-text-secondary mb-2",children:"Outline"}),e.jsx(a,{variant:"outline",children:"Outline Badge"})]})]})};r.parameters={...r.parameters,docs:{...r.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Badge',
    variant: 'default'
  }
}`,...r.parameters?.docs?.source}}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Secondary',
    variant: 'secondary'
  }
}`,...n.parameters?.docs?.source}}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Destructive',
    variant: 'destructive'
  }
}`,...s.parameters?.docs?.source}}};t.parameters={...t.parameters,docs:{...t.parameters?.docs,source:{originalSource:`{
  args: {
    children: 'Outline',
    variant: 'outline'
  }
}`,...t.parameters?.docs?.source}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  render: () => <div className="flex gap-2">\r
      <Badge variant="default">✓ Active</Badge>\r
      <Badge variant="secondary">⏱ Pending</Badge>\r
      <Badge variant="destructive">✕ Inactive</Badge>\r
      <Badge variant="outline">? Unknown</Badge>\r
    </div>
}`,...d.parameters?.docs?.source}}};i.parameters={...i.parameters,docs:{...i.parameters?.docs,source:{originalSource:`{
  render: () => <div className="flex gap-2">\r
      <Badge variant="destructive">🔴 Critical</Badge>\r
      <Badge variant="default">🟠 High</Badge>\r
      <Badge variant="secondary">🟡 Medium</Badge>\r
      <Badge variant="outline">🟢 Low</Badge>\r
    </div>
}`,...i.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  render: () => <div className="flex flex-wrap gap-2">\r
      <Badge variant="default">Design</Badge>\r
      <Badge variant="secondary">Frontend</Badge>\r
      <Badge variant="default">React</Badge>\r
      <Badge variant="secondary">Accessibility</Badge>\r
      <Badge variant="default">Components</Badge>\r
      <Badge variant="secondary">UI</Badge>\r
    </div>
}`,...c.parameters?.docs?.source}}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
  render: () => <div className="flex gap-2">\r
      <Badge variant="default">Comments (5)</Badge>\r
      <Badge variant="secondary">Tasks (12)</Badge>\r
      <Badge variant="destructive">Errors (2)</Badge>\r
      <Badge variant="outline">Warnings (8)</Badge>\r
    </div>
}`,...o.parameters?.docs?.source}}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  render: () => <div className="space-y-4 max-w-md">\r
      <div className="p-4 border rounded-lg">\r
        <div className="flex items-center gap-2 mb-2">\r
          <h3 className="font-semibold">Task Title</h3>\r
          <Badge variant="default">New</Badge>\r
        </div>\r
        <p className="text-sm text-text-secondary mb-3">\r
          Description of the task that needs to be completed.\r
        </p>\r
        <div className="flex gap-2">\r
          <Badge variant="secondary">Design</Badge>\r
          <Badge variant="secondary">In Progress</Badge>\r
        </div>\r
      </div>\r
\r
      <div className="p-4 border rounded-lg">\r
        <div className="flex items-center gap-2 mb-2">\r
          <h3 className="font-semibold">Bug Report</h3>\r
          <Badge variant="destructive">Critical</Badge>\r
        </div>\r
        <p className="text-sm text-text-secondary mb-3">\r
          Critical issue affecting production functionality.\r
        </p>\r
        <div className="flex gap-2">\r
          <Badge variant="destructive">Bug</Badge>\r
          <Badge variant="destructive">Unassigned</Badge>\r
        </div>\r
      </div>\r
    </div>
}`,...l.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  render: () => <div className="flex flex-col gap-4">\r
      <div>\r
        <p className="text-sm font-semibold text-text-secondary mb-2">Default</p>\r
        <Badge variant="default">Default Badge</Badge>\r
      </div>\r
      <div>\r
        <p className="text-sm font-semibold text-text-secondary mb-2">Secondary</p>\r
        <Badge variant="secondary">Secondary Badge</Badge>\r
      </div>\r
      <div>\r
        <p className="text-sm font-semibold text-text-secondary mb-2">Destructive</p>\r
        <Badge variant="destructive">Destructive Badge</Badge>\r
      </div>\r
      <div>\r
        <p className="text-sm font-semibold text-text-secondary mb-2">Outline</p>\r
        <Badge variant="outline">Outline Badge</Badge>\r
      </div>\r
    </div>
}`,...m.parameters?.docs?.source}}};const b=["Default","Secondary","Destructive","Outline","StatusBadges","PriorityBadges","CategoryTags","WithCounts","InContext","AllVariants"];export{m as AllVariants,c as CategoryTags,r as Default,s as Destructive,l as InContext,t as Outline,i as PriorityBadges,n as Secondary,d as StatusBadges,o as WithCounts,b as __namedExportsOrder,j as default};

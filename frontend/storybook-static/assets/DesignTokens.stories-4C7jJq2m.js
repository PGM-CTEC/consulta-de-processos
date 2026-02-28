import{j as e}from"./jsx-runtime-u17CrQMm.js";const x={title:"Design System/Design Tokens",tags:["autodocs"],parameters:{layout:"fullscreen",docs:{description:{component:"Complete design system token documentation including colors, spacing, typography, and effects."}}}},c={render:()=>e.jsxs("div",{className:"p-8 space-y-12",children:[e.jsxs("section",{children:[e.jsx("h2",{className:"text-2xl font-bold text-text-primary mb-6",children:"Brand Colors"}),e.jsxs("div",{className:"grid grid-cols-2 md:grid-cols-4 gap-4",children:[e.jsx(s,{name:"Brand",value:"#4f46e5",cssVar:"--color-brand",desc:"Primary brand color (indigo-600)"}),e.jsx(s,{name:"Brand Hover",value:"#4338ca",cssVar:"--color-brand-hover",desc:"Brand hover state (indigo-700)"}),e.jsx(s,{name:"Brand Light",value:"#e0e7ff",cssVar:"--color-brand-light",desc:"Brand light background (indigo-100)"}),e.jsx(s,{name:"Brand Foreground",value:"#ffffff",cssVar:"--color-brand-fg",desc:"Text on brand backgrounds"})]})]}),e.jsxs("section",{children:[e.jsx("h2",{className:"text-2xl font-bold text-text-primary mb-6",children:"Neutral Palette"}),e.jsxs("div",{className:"grid grid-cols-2 md:grid-cols-4 gap-4",children:[e.jsx(s,{name:"Surface",value:"#ffffff",cssVar:"--color-surface",desc:"Primary background (white)"}),e.jsx(s,{name:"Surface Alt",value:"#f9fafb",cssVar:"--color-surface-alt",desc:"Alternate background (gray-50)"}),e.jsx(s,{name:"Surface Muted",value:"#f3f4f6",cssVar:"--color-surface-muted",desc:"Muted background (gray-100)"}),e.jsx(s,{name:"Border",value:"#e5e7eb",cssVar:"--color-border",desc:"Default border (gray-200)"})]})]}),e.jsxs("section",{children:[e.jsx("h2",{className:"text-2xl font-bold text-text-primary mb-6",children:"Text Colors"}),e.jsx("p",{className:"text-text-secondary mb-4",children:"All text colors meet WCAG AA contrast requirements (minimum 4.5:1 ratio)."}),e.jsxs("div",{className:"grid grid-cols-2 md:grid-cols-4 gap-4",children:[e.jsx(s,{name:"Text Primary",value:"#111827",cssVar:"--color-text-primary",desc:"Main text (gray-900)",textClass:"text-text-primary"}),e.jsx(s,{name:"Text Secondary",value:"#374151",cssVar:"--color-text-secondary",desc:"Secondary text (gray-700)",textClass:"text-text-secondary"}),e.jsx(s,{name:"Text Muted",value:"#4b5563",cssVar:"--color-text-muted",desc:"Muted text (gray-600) — 7.0:1",textClass:"text-text-muted"}),e.jsx(s,{name:"Text Disabled",value:"#9ca3af",cssVar:"--color-text-disabled",desc:"Disabled text (gray-400) — decorative only",textClass:"text-text-disabled"})]})]}),e.jsxs("section",{children:[e.jsx("h2",{className:"text-2xl font-bold text-text-primary mb-6",children:"Semantic Colors"}),e.jsxs("div",{className:"grid grid-cols-2 md:grid-cols-4 gap-4",children:[e.jsx(s,{name:"Success",value:"#059669",cssVar:"--color-success",desc:"Success state (emerald-600)"}),e.jsx(s,{name:"Success BG",value:"#d1fae5",cssVar:"--color-success-bg",desc:"Success background (emerald-100)"}),e.jsx(s,{name:"Error",value:"#dc2626",cssVar:"--color-error",desc:"Error state (red-600)"}),e.jsx(s,{name:"Error BG",value:"#fee2e2",cssVar:"--color-error-bg",desc:"Error background (red-100)"}),e.jsx(s,{name:"Warning",value:"#d97706",cssVar:"--color-warning",desc:"Warning state (amber-600)"}),e.jsx(s,{name:"Warning BG",value:"#fef3c7",cssVar:"--color-warning-bg",desc:"Warning background (amber-100)"}),e.jsx(s,{name:"Info",value:"#2563eb",cssVar:"--color-info",desc:"Info state (blue-600)"}),e.jsx(s,{name:"Info BG",value:"#dbeafe",cssVar:"--color-info-bg",desc:"Info background (blue-100)"})]})]})]})},o={render:()=>e.jsx("div",{className:"p-8 space-y-8",children:e.jsxs("section",{children:[e.jsx("h2",{className:"text-2xl font-bold text-text-primary mb-6",children:"Spacing Scale"}),e.jsx("p",{className:"text-text-secondary mb-6",children:"Consistent spacing scale based on 4px base unit. Used for margins, padding, and gaps."}),e.jsx("div",{className:"space-y-4",children:[{name:"--space-1",value:"0.25rem (4px)",px:"w-1"},{name:"--space-2",value:"0.5rem (8px)",px:"w-2"},{name:"--space-3",value:"0.75rem (12px)",px:"w-3"},{name:"--space-4",value:"1rem (16px)",px:"w-4"},{name:"--space-6",value:"1.5rem (24px)",px:"w-6"},{name:"--space-8",value:"2rem (32px)",px:"w-8"},{name:"--space-12",value:"3rem (48px)",px:"w-12"}].map(({name:a,value:r,px:t})=>e.jsxs("div",{className:"flex items-center gap-4",children:[e.jsx("div",{className:"min-w-32",children:e.jsx("code",{className:"text-sm font-mono text-primary",children:a})}),e.jsx("div",{className:`${t} bg-primary rounded`}),e.jsx("span",{className:"text-text-secondary text-sm",children:r})]},a))})]})})},d={render:()=>e.jsxs("div",{className:"p-8 space-y-8",children:[e.jsxs("section",{children:[e.jsx("h2",{className:"text-2xl font-bold text-text-primary mb-6",children:"Font Sizes"}),e.jsx("div",{className:"space-y-4",children:[{name:"--font-size-xs",size:"0.75rem (12px)",className:"text-xs"},{name:"--font-size-sm",size:"0.875rem (14px)",className:"text-sm"},{name:"--font-size-base",size:"1rem (16px)",className:"text-base"},{name:"--font-size-lg",size:"1.125rem (18px)",className:"text-lg"},{name:"--font-size-xl",size:"1.25rem (20px)",className:"text-xl"},{name:"--font-size-2xl",size:"1.5rem (24px)",className:"text-2xl"}].map(({name:a,size:r,className:t})=>e.jsxs("div",{children:[e.jsx("code",{className:"text-xs text-primary",children:a}),e.jsx("p",{className:`${t} text-text-primary my-2`,children:"The quick brown fox jumps over the lazy dog"}),e.jsx("span",{className:"text-xs text-text-secondary",children:r})]},a))})]}),e.jsxs("section",{children:[e.jsx("h2",{className:"text-2xl font-bold text-text-primary mb-6",children:"Font Weights"}),e.jsx("div",{className:"space-y-3",children:[{name:"--font-weight-normal",weight:"400",className:"font-normal"},{name:"--font-weight-medium",weight:"500",className:"font-medium"},{name:"--font-weight-semibold",weight:"600",className:"font-semibold"},{name:"--font-weight-bold",weight:"700",className:"font-bold"},{name:"--font-weight-extrabold",weight:"800",className:"font-extrabold"}].map(({name:a,weight:r,className:t})=>e.jsxs("div",{children:[e.jsx("p",{className:`${t} text-base text-text-primary`,children:"The quick brown fox jumps"}),e.jsxs("code",{className:"text-xs text-primary",children:[a,": ",r]})]},a))})]})]})},n={render:()=>e.jsxs("div",{className:"p-8 space-y-12",children:[e.jsxs("section",{children:[e.jsx("h2",{className:"text-2xl font-bold text-text-primary mb-6",children:"Shadows"}),e.jsxs("div",{className:"grid grid-cols-1 md:grid-cols-3 gap-6",children:[e.jsxs("div",{className:"p-6 bg-surface rounded-lg shadow-sm border border-border",children:[e.jsx("p",{className:"text-sm text-text-secondary mb-2",children:"Small Shadow"}),e.jsx("p",{className:"font-mono text-xs text-primary",children:"--shadow-sm"})]}),e.jsxs("div",{className:"p-6 bg-surface rounded-lg shadow-md border border-border",children:[e.jsx("p",{className:"text-sm text-text-secondary mb-2",children:"Medium Shadow"}),e.jsx("p",{className:"font-mono text-xs text-primary",children:"--shadow-md"})]}),e.jsxs("div",{className:"p-6 bg-surface rounded-lg shadow-lg border border-border",children:[e.jsx("p",{className:"text-sm text-text-secondary mb-2",children:"Large Shadow"}),e.jsx("p",{className:"font-mono text-xs text-primary",children:"--shadow-lg"})]})]})]}),e.jsxs("section",{children:[e.jsx("h2",{className:"text-2xl font-bold text-text-primary mb-6",children:"Border Radius"}),e.jsx("div",{className:"grid grid-cols-2 md:grid-cols-5 gap-4",children:[{name:"--radius-sm",class:"rounded-sm"},{name:"--radius-md",class:"rounded-md"},{name:"--radius-lg",class:"rounded-lg"},{name:"--radius-xl",class:"rounded-xl"},{name:"--radius-full",class:"rounded-full"}].map(({name:a,class:r})=>e.jsxs("div",{children:[e.jsx("div",{className:`${r} w-20 h-20 bg-primary mb-2`}),e.jsx("code",{className:"text-xs text-primary block",children:a})]},a))})]})]})};function s({name:a,value:r,cssVar:t,desc:l,textClass:m}){return e.jsxs("div",{className:"space-y-2",children:[e.jsx("div",{className:"w-full h-24 rounded-lg border-2 border-border shadow-sm",style:{backgroundColor:r}}),e.jsxs("div",{children:[e.jsx("h4",{className:`font-semibold text-sm ${m||"text-text-primary"}`,children:a}),e.jsx("code",{className:"text-xs text-primary block",children:t}),e.jsx("code",{className:"text-xs text-text-secondary block",children:r}),e.jsx("p",{className:"text-xs text-text-secondary mt-1",children:l})]})]})}c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  render: () => <div className="p-8 space-y-12">\r
      {/* Brand Colors */}\r
      <section>\r
        <h2 className="text-2xl font-bold text-text-primary mb-6">Brand Colors</h2>\r
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">\r
          <ColorSwatch name="Brand" value="#4f46e5" cssVar="--color-brand" desc="Primary brand color (indigo-600)" />\r
          <ColorSwatch name="Brand Hover" value="#4338ca" cssVar="--color-brand-hover" desc="Brand hover state (indigo-700)" />\r
          <ColorSwatch name="Brand Light" value="#e0e7ff" cssVar="--color-brand-light" desc="Brand light background (indigo-100)" />\r
          <ColorSwatch name="Brand Foreground" value="#ffffff" cssVar="--color-brand-fg" desc="Text on brand backgrounds" />\r
        </div>\r
      </section>\r
\r
      {/* Neutral Palette */}\r
      <section>\r
        <h2 className="text-2xl font-bold text-text-primary mb-6">Neutral Palette</h2>\r
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">\r
          <ColorSwatch name="Surface" value="#ffffff" cssVar="--color-surface" desc="Primary background (white)" />\r
          <ColorSwatch name="Surface Alt" value="#f9fafb" cssVar="--color-surface-alt" desc="Alternate background (gray-50)" />\r
          <ColorSwatch name="Surface Muted" value="#f3f4f6" cssVar="--color-surface-muted" desc="Muted background (gray-100)" />\r
          <ColorSwatch name="Border" value="#e5e7eb" cssVar="--color-border" desc="Default border (gray-200)" />\r
        </div>\r
      </section>\r
\r
      {/* Text Colors */}\r
      <section>\r
        <h2 className="text-2xl font-bold text-text-primary mb-6">Text Colors</h2>\r
        <p className="text-text-secondary mb-4">\r
          All text colors meet WCAG AA contrast requirements (minimum 4.5:1 ratio).\r
        </p>\r
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">\r
          <ColorSwatch name="Text Primary" value="#111827" cssVar="--color-text-primary" desc="Main text (gray-900)" textClass="text-text-primary" />\r
          <ColorSwatch name="Text Secondary" value="#374151" cssVar="--color-text-secondary" desc="Secondary text (gray-700)" textClass="text-text-secondary" />\r
          <ColorSwatch name="Text Muted" value="#4b5563" cssVar="--color-text-muted" desc="Muted text (gray-600) — 7.0:1" textClass="text-text-muted" />\r
          <ColorSwatch name="Text Disabled" value="#9ca3af" cssVar="--color-text-disabled" desc="Disabled text (gray-400) — decorative only" textClass="text-text-disabled" />\r
        </div>\r
      </section>\r
\r
      {/* Semantic Colors */}\r
      <section>\r
        <h2 className="text-2xl font-bold text-text-primary mb-6">Semantic Colors</h2>\r
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">\r
          <ColorSwatch name="Success" value="#059669" cssVar="--color-success" desc="Success state (emerald-600)" />\r
          <ColorSwatch name="Success BG" value="#d1fae5" cssVar="--color-success-bg" desc="Success background (emerald-100)" />\r
          <ColorSwatch name="Error" value="#dc2626" cssVar="--color-error" desc="Error state (red-600)" />\r
          <ColorSwatch name="Error BG" value="#fee2e2" cssVar="--color-error-bg" desc="Error background (red-100)" />\r
          <ColorSwatch name="Warning" value="#d97706" cssVar="--color-warning" desc="Warning state (amber-600)" />\r
          <ColorSwatch name="Warning BG" value="#fef3c7" cssVar="--color-warning-bg" desc="Warning background (amber-100)" />\r
          <ColorSwatch name="Info" value="#2563eb" cssVar="--color-info" desc="Info state (blue-600)" />\r
          <ColorSwatch name="Info BG" value="#dbeafe" cssVar="--color-info-bg" desc="Info background (blue-100)" />\r
        </div>\r
      </section>\r
    </div>
}`,...c.parameters?.docs?.source}}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
  render: () => <div className="p-8 space-y-8">\r
      <section>\r
        <h2 className="text-2xl font-bold text-text-primary mb-6">Spacing Scale</h2>\r
        <p className="text-text-secondary mb-6">\r
          Consistent spacing scale based on 4px base unit. Used for margins, padding, and gaps.\r
        </p>\r
        <div className="space-y-4">\r
          {[{
          name: '--space-1',
          value: '0.25rem (4px)',
          px: 'w-1'
        }, {
          name: '--space-2',
          value: '0.5rem (8px)',
          px: 'w-2'
        }, {
          name: '--space-3',
          value: '0.75rem (12px)',
          px: 'w-3'
        }, {
          name: '--space-4',
          value: '1rem (16px)',
          px: 'w-4'
        }, {
          name: '--space-6',
          value: '1.5rem (24px)',
          px: 'w-6'
        }, {
          name: '--space-8',
          value: '2rem (32px)',
          px: 'w-8'
        }, {
          name: '--space-12',
          value: '3rem (48px)',
          px: 'w-12'
        }].map(({
          name,
          value,
          px
        }) => <div key={name} className="flex items-center gap-4">\r
              <div className="min-w-32">\r
                <code className="text-sm font-mono text-primary">{name}</code>\r
              </div>\r
              <div className={\`\${px} bg-primary rounded\`} />\r
              <span className="text-text-secondary text-sm">{value}</span>\r
            </div>)}\r
        </div>\r
      </section>\r
    </div>
}`,...o.parameters?.docs?.source}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  render: () => <div className="p-8 space-y-8">\r
      <section>\r
        <h2 className="text-2xl font-bold text-text-primary mb-6">Font Sizes</h2>\r
        <div className="space-y-4">\r
          {[{
          name: '--font-size-xs',
          size: '0.75rem (12px)',
          className: 'text-xs'
        }, {
          name: '--font-size-sm',
          size: '0.875rem (14px)',
          className: 'text-sm'
        }, {
          name: '--font-size-base',
          size: '1rem (16px)',
          className: 'text-base'
        }, {
          name: '--font-size-lg',
          size: '1.125rem (18px)',
          className: 'text-lg'
        }, {
          name: '--font-size-xl',
          size: '1.25rem (20px)',
          className: 'text-xl'
        }, {
          name: '--font-size-2xl',
          size: '1.5rem (24px)',
          className: 'text-2xl'
        }].map(({
          name,
          size,
          className: cls
        }) => <div key={name}>\r
              <code className="text-xs text-primary">{name}</code>\r
              <p className={\`\${cls} text-text-primary my-2\`}>The quick brown fox jumps over the lazy dog</p>\r
              <span className="text-xs text-text-secondary">{size}</span>\r
            </div>)}\r
        </div>\r
      </section>\r
\r
      <section>\r
        <h2 className="text-2xl font-bold text-text-primary mb-6">Font Weights</h2>\r
        <div className="space-y-3">\r
          {[{
          name: '--font-weight-normal',
          weight: '400',
          className: 'font-normal'
        }, {
          name: '--font-weight-medium',
          weight: '500',
          className: 'font-medium'
        }, {
          name: '--font-weight-semibold',
          weight: '600',
          className: 'font-semibold'
        }, {
          name: '--font-weight-bold',
          weight: '700',
          className: 'font-bold'
        }, {
          name: '--font-weight-extrabold',
          weight: '800',
          className: 'font-extrabold'
        }].map(({
          name,
          weight,
          className: cls
        }) => <div key={name}>\r
              <p className={\`\${cls} text-base text-text-primary\`}>The quick brown fox jumps</p>\r
              <code className="text-xs text-primary">{name}: {weight}</code>\r
            </div>)}\r
        </div>\r
      </section>\r
    </div>
}`,...d.parameters?.docs?.source}}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
  render: () => <div className="p-8 space-y-12">\r
      <section>\r
        <h2 className="text-2xl font-bold text-text-primary mb-6">Shadows</h2>\r
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">\r
          <div className="p-6 bg-surface rounded-lg shadow-sm border border-border">\r
            <p className="text-sm text-text-secondary mb-2">Small Shadow</p>\r
            <p className="font-mono text-xs text-primary">--shadow-sm</p>\r
          </div>\r
          <div className="p-6 bg-surface rounded-lg shadow-md border border-border">\r
            <p className="text-sm text-text-secondary mb-2">Medium Shadow</p>\r
            <p className="font-mono text-xs text-primary">--shadow-md</p>\r
          </div>\r
          <div className="p-6 bg-surface rounded-lg shadow-lg border border-border">\r
            <p className="text-sm text-text-secondary mb-2">Large Shadow</p>\r
            <p className="font-mono text-xs text-primary">--shadow-lg</p>\r
          </div>\r
        </div>\r
      </section>\r
\r
      <section>\r
        <h2 className="text-2xl font-bold text-text-primary mb-6">Border Radius</h2>\r
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">\r
          {[{
          name: '--radius-sm',
          class: 'rounded-sm'
        }, {
          name: '--radius-md',
          class: 'rounded-md'
        }, {
          name: '--radius-lg',
          class: 'rounded-lg'
        }, {
          name: '--radius-xl',
          class: 'rounded-xl'
        }, {
          name: '--radius-full',
          class: 'rounded-full'
        }].map(({
          name,
          class: cls
        }) => <div key={name}>\r
              <div className={\`\${cls} w-20 h-20 bg-primary mb-2\`} />\r
              <code className="text-xs text-primary block">{name}</code>\r
            </div>)}\r
        </div>\r
      </section>\r
    </div>
}`,...n.parameters?.docs?.source}}};const p=["ColorPalette","Spacing","Typography","Effects"];export{c as ColorPalette,n as Effects,o as Spacing,d as Typography,p as __namedExportsOrder,x as default};

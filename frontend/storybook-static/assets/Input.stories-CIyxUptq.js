import{j as e}from"./jsx-runtime-u17CrQMm.js";import{c as g}from"./utils-BQHNewu7.js";function r({className:a,type:v,...f}){return e.jsx("input",{type:v,className:g("flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",a),...f})}r.__docgenInfo={description:"",methods:[],displayName:"Input"};const j={title:"Components/Input",component:r,tags:["autodocs"],parameters:{layout:"centered",docs:{description:{component:`Input Component — Atomic Design System\r

Accessible text input field with support for various states and types.\r

**Features:**\r
- Full keyboard navigation support\r
- Focus indicators (focus-visible ring)\r
- Disabled state with reduced opacity\r
- Placeholder text styling\r
- Support for all standard input types\r
- Dark mode support\r
- WCAG AA compliant\r

**Input Types Supported:**\r
- text (default)\r
- email\r
- password\r
- number\r
- search\r
- tel\r
- url\r
- date\r
- time\r
- checkbox\r
- radio`}}},argTypes:{type:{control:"select",options:["text","email","password","number","search","tel","url","date","time"],description:"HTML input type"},placeholder:{control:"text",description:"Placeholder text"},disabled:{control:"boolean",description:"Disable input interactions"}}},t={args:{type:"text",placeholder:"Enter text..."}},s={args:{type:"email",placeholder:"your@email.com"}},l={args:{type:"password",placeholder:"Enter password..."}},n={args:{type:"number",placeholder:"Enter a number..."}},o={args:{type:"search",placeholder:"Search..."}},m={args:{type:"tel",placeholder:"(123) 456-7890"}},c={args:{type:"url",placeholder:"https://example.com"}},d={args:{type:"date"}},p={args:{type:"time"}},i={args:{type:"text",placeholder:"This input is disabled",disabled:!0}},u={args:{type:"text",placeholder:"Placeholder text",defaultValue:"Pre-filled value"}},x={render:()=>e.jsxs("form",{className:"w-full max-w-md space-y-4",children:[e.jsxs("div",{children:[e.jsx("label",{htmlFor:"name",className:"block text-sm font-medium text-text-primary mb-2",children:"Full Name"}),e.jsx(r,{id:"name",type:"text",placeholder:"John Doe"})]}),e.jsxs("div",{children:[e.jsx("label",{htmlFor:"email",className:"block text-sm font-medium text-text-primary mb-2",children:"Email Address"}),e.jsx(r,{id:"email",type:"email",placeholder:"john@example.com"})]}),e.jsxs("div",{children:[e.jsx("label",{htmlFor:"phone",className:"block text-sm font-medium text-text-primary mb-2",children:"Phone Number"}),e.jsx(r,{id:"phone",type:"tel",placeholder:"(123) 456-7890"})]}),e.jsxs("div",{children:[e.jsx("label",{htmlFor:"password",className:"block text-sm font-medium text-text-primary mb-2",children:"Password"}),e.jsx(r,{id:"password",type:"password",placeholder:"••••••••"})]})]})},h={render:()=>e.jsxs("div",{className:"w-full max-w-md",children:[e.jsx("label",{htmlFor:"search",className:"block text-sm font-medium text-text-primary mb-2",children:"Search"}),e.jsxs("div",{className:"relative",children:[e.jsx(r,{id:"search",type:"search",placeholder:"Search processes, cases...",className:"pl-10"}),e.jsx("span",{className:"absolute left-3 top-1/2 -translate-y-1/2 text-text-muted",children:"🔍"})]})]})},b={render:()=>e.jsxs("div",{className:"w-full max-w-md space-y-4",children:[e.jsxs("div",{children:[e.jsx("label",{htmlFor:"valid",className:"block text-sm font-medium text-text-primary mb-2",children:"Valid Input"}),e.jsx(r,{id:"valid",type:"text",defaultValue:"john@example.com",className:"border-success"}),e.jsx("p",{className:"text-xs text-success mt-1",children:"✓ Input is valid"})]}),e.jsxs("div",{children:[e.jsx("label",{htmlFor:"invalid",className:"block text-sm font-medium text-text-primary mb-2",children:"Invalid Input"}),e.jsx(r,{id:"invalid",type:"email",defaultValue:"not-an-email",className:"border-error"}),e.jsx("p",{className:"text-xs text-error mt-1",children:"✕ Please enter a valid email"})]}),e.jsxs("div",{children:[e.jsx("label",{htmlFor:"warning",className:"block text-sm font-medium text-text-primary mb-2",children:"Warning Input"}),e.jsx(r,{id:"warning",type:"text",defaultValue:"Some value",className:"border-warning"}),e.jsx("p",{className:"text-xs text-warning mt-1",children:"⚠ This field needs review"})]})]})},y={render:()=>e.jsx("div",{className:"w-full max-w-md space-y-4",children:[{type:"text",label:"Text",placeholder:"Text input"},{type:"email",label:"Email",placeholder:"email@example.com"},{type:"password",label:"Password",placeholder:"••••••••"},{type:"number",label:"Number",placeholder:"0"},{type:"search",label:"Search",placeholder:"Search..."},{type:"tel",label:"Telephone",placeholder:"(123) 456-7890"},{type:"url",label:"URL",placeholder:"https://example.com"},{type:"date",label:"Date"},{type:"time",label:"Time"}].map(({type:a,label:v,placeholder:f})=>e.jsxs("div",{children:[e.jsx("label",{className:"block text-sm font-medium text-text-primary mb-2",children:v}),e.jsx(r,{type:a,placeholder:f})]},a))})};t.parameters={...t.parameters,docs:{...t.parameters?.docs,source:{originalSource:`{
  args: {
    type: 'text',
    placeholder: 'Enter text...'
  }
}`,...t.parameters?.docs?.source}}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
  args: {
    type: 'email',
    placeholder: 'your@email.com'
  }
}`,...s.parameters?.docs?.source}}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  args: {
    type: 'password',
    placeholder: 'Enter password...'
  }
}`,...l.parameters?.docs?.source}}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
  args: {
    type: 'number',
    placeholder: 'Enter a number...'
  }
}`,...n.parameters?.docs?.source}}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
  args: {
    type: 'search',
    placeholder: 'Search...'
  }
}`,...o.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    type: 'tel',
    placeholder: '(123) 456-7890'
  }
}`,...m.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    type: 'url',
    placeholder: 'https://example.com'
  }
}`,...c.parameters?.docs?.source}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    type: 'date'
  }
}`,...d.parameters?.docs?.source}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    type: 'time'
  }
}`,...p.parameters?.docs?.source}}};i.parameters={...i.parameters,docs:{...i.parameters?.docs,source:{originalSource:`{
  args: {
    type: 'text',
    placeholder: 'This input is disabled',
    disabled: true
  }
}`,...i.parameters?.docs?.source}}};u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  args: {
    type: 'text',
    placeholder: 'Placeholder text',
    defaultValue: 'Pre-filled value'
  }
}`,...u.parameters?.docs?.source}}};x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  render: () => <form className="w-full max-w-md space-y-4">\r
      <div>\r
        <label htmlFor="name" className="block text-sm font-medium text-text-primary mb-2">\r
          Full Name\r
        </label>\r
        <Input id="name" type="text" placeholder="John Doe" />\r
      </div>\r
\r
      <div>\r
        <label htmlFor="email" className="block text-sm font-medium text-text-primary mb-2">\r
          Email Address\r
        </label>\r
        <Input id="email" type="email" placeholder="john@example.com" />\r
      </div>\r
\r
      <div>\r
        <label htmlFor="phone" className="block text-sm font-medium text-text-primary mb-2">\r
          Phone Number\r
        </label>\r
        <Input id="phone" type="tel" placeholder="(123) 456-7890" />\r
      </div>\r
\r
      <div>\r
        <label htmlFor="password" className="block text-sm font-medium text-text-primary mb-2">\r
          Password\r
        </label>\r
        <Input id="password" type="password" placeholder="••••••••" />\r
      </div>\r
    </form>
}`,...x.parameters?.docs?.source}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  render: () => <div className="w-full max-w-md">\r
      <label htmlFor="search" className="block text-sm font-medium text-text-primary mb-2">\r
        Search\r
      </label>\r
      <div className="relative">\r
        <Input id="search" type="search" placeholder="Search processes, cases..." className="pl-10" />\r
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted">🔍</span>\r
      </div>\r
    </div>
}`,...h.parameters?.docs?.source}}};b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  render: () => <div className="w-full max-w-md space-y-4">\r
      <div>\r
        <label htmlFor="valid" className="block text-sm font-medium text-text-primary mb-2">\r
          Valid Input\r
        </label>\r
        <Input id="valid" type="text" defaultValue="john@example.com" className="border-success" />\r
        <p className="text-xs text-success mt-1">✓ Input is valid</p>\r
      </div>\r
\r
      <div>\r
        <label htmlFor="invalid" className="block text-sm font-medium text-text-primary mb-2">\r
          Invalid Input\r
        </label>\r
        <Input id="invalid" type="email" defaultValue="not-an-email" className="border-error" />\r
        <p className="text-xs text-error mt-1">✕ Please enter a valid email</p>\r
      </div>\r
\r
      <div>\r
        <label htmlFor="warning" className="block text-sm font-medium text-text-primary mb-2">\r
          Warning Input\r
        </label>\r
        <Input id="warning" type="text" defaultValue="Some value" className="border-warning" />\r
        <p className="text-xs text-warning mt-1">⚠ This field needs review</p>\r
      </div>\r
    </div>
}`,...b.parameters?.docs?.source}}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  render: () => <div className="w-full max-w-md space-y-4">\r
      {[{
      type: 'text',
      label: 'Text',
      placeholder: 'Text input'
    }, {
      type: 'email',
      label: 'Email',
      placeholder: 'email@example.com'
    }, {
      type: 'password',
      label: 'Password',
      placeholder: '••••••••'
    }, {
      type: 'number',
      label: 'Number',
      placeholder: '0'
    }, {
      type: 'search',
      label: 'Search',
      placeholder: 'Search...'
    }, {
      type: 'tel',
      label: 'Telephone',
      placeholder: '(123) 456-7890'
    }, {
      type: 'url',
      label: 'URL',
      placeholder: 'https://example.com'
    }, {
      type: 'date',
      label: 'Date'
    }, {
      type: 'time',
      label: 'Time'
    }].map(({
      type,
      label,
      placeholder
    }) => <div key={type}>\r
          <label className="block text-sm font-medium text-text-primary mb-2">\r
            {label}\r
          </label>\r
          <Input type={type} placeholder={placeholder} />\r
        </div>)}\r
    </div>
}`,...y.parameters?.docs?.source}}};const S=["Text","Email","Password","Number","Search","Telephone","URL","Date","Time","Disabled","WithValue","FormGroup","SearchForm","ValidationStates","AllTypes"];export{y as AllTypes,d as Date,i as Disabled,s as Email,x as FormGroup,n as Number,l as Password,o as Search,h as SearchForm,m as Telephone,t as Text,p as Time,c as URL,b as ValidationStates,u as WithValue,S as __namedExportsOrder,j as default};

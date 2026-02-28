import{j as e}from"./jsx-runtime-u17CrQMm.js";import{c as i}from"./utils-BQHNewu7.js";import{B as o}from"./button-D3x7JmdK.js";import"./index-LHNt3CwB.js";function s({className:r,...a}){return e.jsx("div",{className:i("rounded-xl border bg-card text-card-foreground shadow",r),...a})}function t({className:r,...a}){return e.jsx("div",{className:i("flex flex-col space-y-1.5 p-6",r),...a})}function d({className:r,...a}){return e.jsx("h3",{className:i("font-semibold leading-none tracking-tight",r),...a})}function n({className:r,...a}){return e.jsx("div",{className:i("p-6 pt-0",r),...a})}function h({className:r,...a}){return e.jsx("div",{className:i("flex items-center p-6 pt-0",r),...a})}s.__docgenInfo={description:"",methods:[],displayName:"Card"};t.__docgenInfo={description:"",methods:[],displayName:"CardHeader"};d.__docgenInfo={description:"",methods:[],displayName:"CardTitle"};n.__docgenInfo={description:"",methods:[],displayName:"CardContent"};h.__docgenInfo={description:"",methods:[],displayName:"CardFooter"};const y={title:"Components/Card",component:s,tags:["autodocs"],parameters:{layout:"centered",docs:{description:{component:`Card Component — Atomic Design System\r

Composable card container with semantic sections:\r
- Card: Root container with border, shadow, and rounded corners\r
- CardHeader: Top section with spacing\r
- CardTitle: Header text with typography\r
- CardContent: Main content area\r
- CardFooter: Bottom action area with flex layout\r

**Features:**\r
- Responsive shadow and rounded corners\r
- Flexbox footer for button alignment\r
- Semantic HTML structure\r
- Tailwind CSS design tokens integration`}}}},c={render:()=>e.jsxs(s,{className:"w-[350px]",children:[e.jsx(t,{children:e.jsx(d,{children:"Basic Card"})}),e.jsx(n,{children:e.jsx("p",{children:"This is a simple card with header and content."})})]})},l={render:()=>e.jsxs(s,{className:"w-[350px]",children:[e.jsx(t,{children:e.jsx(d,{children:"Card with Actions"})}),e.jsx(n,{children:e.jsx("p",{children:"This card includes action buttons in the footer section."})}),e.jsxs(h,{className:"flex gap-2",children:[e.jsx(o,{variant:"secondary",children:"Cancel"}),e.jsx(o,{children:"Save"})]})]})},m={render:()=>e.jsxs(s,{className:"w-[400px]",children:[e.jsx(t,{children:e.jsx(d,{children:"Full Featured Card"})}),e.jsx(n,{className:"space-y-4",children:e.jsxs("div",{children:[e.jsx("h4",{className:"font-semibold mb-2",children:"Features"}),e.jsxs("ul",{className:"list-disc list-inside text-sm text-text-secondary",children:[e.jsx("li",{children:"Semantic HTML structure"}),e.jsx("li",{children:"Responsive design"}),e.jsx("li",{children:"Dark mode support"}),e.jsx("li",{children:"Accessibility focused"})]})]})}),e.jsxs(h,{className:"flex gap-2 justify-end",children:[e.jsx(o,{variant:"outline",children:"Learn More"}),e.jsx(o,{children:"Get Started"})]})]})},p={render:()=>e.jsx(s,{className:"w-[300px]",children:e.jsx(n,{className:"pt-6",children:e.jsxs("div",{className:"text-center",children:[e.jsx("div",{className:"text-3xl font-bold text-primary",children:"42"}),e.jsx("p",{className:"text-sm text-text-secondary mt-2",children:"Total Items"})]})})})},x={render:()=>e.jsx("div",{className:"grid grid-cols-3 gap-4 w-full max-w-4xl",children:[1,2,3,4,5,6].map(r=>e.jsx(s,{className:"h-full",children:e.jsx(n,{className:"pt-6",children:e.jsxs("div",{className:"text-center",children:[e.jsxs("div",{className:"text-2xl font-bold text-primary",children:["Card ",r]}),e.jsx("p",{className:"text-xs text-text-secondary mt-2",children:"Sample card"})]})})},r))})},u={render:()=>e.jsxs(s,{className:"w-[350px] overflow-hidden",children:[e.jsx("div",{className:"h-48 bg-gradient-to-br from-primary to-secondary"}),e.jsx(t,{children:e.jsx(d,{children:"Image Card"})}),e.jsx(n,{children:e.jsx("p",{className:"text-sm text-text-secondary",children:"Cards can include images or hero sections at the top."})})]})},C={render:()=>e.jsxs(s,{className:"w-[400px]",children:[e.jsx(t,{children:e.jsx(d,{children:"Sign In"})}),e.jsxs(n,{className:"space-y-4",children:[e.jsxs("div",{children:[e.jsx("label",{htmlFor:"email",className:"block text-sm font-medium mb-1",children:"Email"}),e.jsx("input",{id:"email",type:"email",placeholder:"your@email.com",className:"w-full px-3 py-2 border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"})]}),e.jsxs("div",{children:[e.jsx("label",{htmlFor:"password",className:"block text-sm font-medium mb-1",children:"Password"}),e.jsx("input",{id:"password",type:"password",placeholder:"••••••••",className:"w-full px-3 py-2 border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"})]})]}),e.jsx(h,{children:e.jsx(o,{className:"w-full",children:"Sign In"})})]})};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  render: () => <Card className="w-[350px]">\r
      <CardHeader>\r
        <CardTitle>Basic Card</CardTitle>\r
      </CardHeader>\r
      <CardContent>\r
        <p>This is a simple card with header and content.</p>\r
      </CardContent>\r
    </Card>
}`,...c.parameters?.docs?.source}}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  render: () => <Card className="w-[350px]">\r
      <CardHeader>\r
        <CardTitle>Card with Actions</CardTitle>\r
      </CardHeader>\r
      <CardContent>\r
        <p>This card includes action buttons in the footer section.</p>\r
      </CardContent>\r
      <CardFooter className="flex gap-2">\r
        <Button variant="secondary">Cancel</Button>\r
        <Button>Save</Button>\r
      </CardFooter>\r
    </Card>
}`,...l.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  render: () => <Card className="w-[400px]">\r
      <CardHeader>\r
        <CardTitle>Full Featured Card</CardTitle>\r
      </CardHeader>\r
      <CardContent className="space-y-4">\r
        <div>\r
          <h4 className="font-semibold mb-2">Features</h4>\r
          <ul className="list-disc list-inside text-sm text-text-secondary">\r
            <li>Semantic HTML structure</li>\r
            <li>Responsive design</li>\r
            <li>Dark mode support</li>\r
            <li>Accessibility focused</li>\r
          </ul>\r
        </div>\r
      </CardContent>\r
      <CardFooter className="flex gap-2 justify-end">\r
        <Button variant="outline">Learn More</Button>\r
        <Button>Get Started</Button>\r
      </CardFooter>\r
    </Card>
}`,...m.parameters?.docs?.source}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  render: () => <Card className="w-[300px]">\r
      <CardContent className="pt-6">\r
        <div className="text-center">\r
          <div className="text-3xl font-bold text-primary">42</div>\r
          <p className="text-sm text-text-secondary mt-2">Total Items</p>\r
        </div>\r
      </CardContent>\r
    </Card>
}`,...p.parameters?.docs?.source}}};x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  render: () => <div className="grid grid-cols-3 gap-4 w-full max-w-4xl">\r
      {[1, 2, 3, 4, 5, 6].map(num => <Card key={num} className="h-full">\r
          <CardContent className="pt-6">\r
            <div className="text-center">\r
              <div className="text-2xl font-bold text-primary">Card {num}</div>\r
              <p className="text-xs text-text-secondary mt-2">Sample card</p>\r
            </div>\r
          </CardContent>\r
        </Card>)}\r
    </div>
}`,...x.parameters?.docs?.source}}};u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  render: () => <Card className="w-[350px] overflow-hidden">\r
      <div className="h-48 bg-gradient-to-br from-primary to-secondary" />\r
      <CardHeader>\r
        <CardTitle>Image Card</CardTitle>\r
      </CardHeader>\r
      <CardContent>\r
        <p className="text-sm text-text-secondary">\r
          Cards can include images or hero sections at the top.\r
        </p>\r
      </CardContent>\r
    </Card>
}`,...u.parameters?.docs?.source}}};C.parameters={...C.parameters,docs:{...C.parameters?.docs,source:{originalSource:`{
  render: () => <Card className="w-[400px]">\r
      <CardHeader>\r
        <CardTitle>Sign In</CardTitle>\r
      </CardHeader>\r
      <CardContent className="space-y-4">\r
        <div>\r
          <label htmlFor="email" className="block text-sm font-medium mb-1">\r
            Email\r
          </label>\r
          <input id="email" type="email" placeholder="your@email.com" className="w-full px-3 py-2 border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring" />\r
        </div>\r
        <div>\r
          <label htmlFor="password" className="block text-sm font-medium mb-1">\r
            Password\r
          </label>\r
          <input id="password" type="password" placeholder="••••••••" className="w-full px-3 py-2 border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring" />\r
        </div>\r
      </CardContent>\r
      <CardFooter>\r
        <Button className="w-full">Sign In</Button>\r
      </CardFooter>\r
    </Card>
}`,...C.parameters?.docs?.source}}};const b=["BasicCard","CardWithActions","FullFeaturedCard","CompactCard","CardGrid","CardWithImage","FormCard"];export{c as BasicCard,x as CardGrid,l as CardWithActions,u as CardWithImage,p as CompactCard,C as FormCard,m as FullFeaturedCard,b as __namedExportsOrder,y as default};

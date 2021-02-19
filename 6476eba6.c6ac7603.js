(window.webpackJsonp=window.webpackJsonp||[]).push([[15],{114:function(e,t,n){"use strict";n.r(t),n.d(t,"frontMatter",(function(){return c})),n.d(t,"metadata",(function(){return i})),n.d(t,"rightToc",(function(){return p})),n.d(t,"default",(function(){return s}));var r=n(2),a=n(6),o=(n(0),n(134)),c={id:"doc6",title:"Usage"},i={id:"doc6",isDocsHomePage:!1,title:"Usage",description:"On Python => 2.7 run",source:"@site/docs/usage.md",permalink:"/bats/docs/doc6",editUrl:"https://github.com/facebook/docusaurus/edit/master/website/docs/usage.md",sidebar:"someSidebar",previous:{title:"Folder structure",permalink:"/bats/docs/doc5"},next:{title:"Logs",permalink:"/bats/docs/doc7"}},p=[{value:"Params:",id:"params",children:[]}],l={rightToc:p};function s(e){var t=e.components,n=Object(a.a)(e,["components"]);return Object(o.b)("wrapper",Object(r.a)({},l,n,{components:t,mdxType:"MDXLayout"}),Object(o.b)("p",null,"On Python => 2.7 run\n",Object(o.b)("inlineCode",{parentName:"p"},"python -m bats")),Object(o.b)("p",null,"On Python <2.7 (POD it is 2.6) run ",Object(o.b)("inlineCode",{parentName:"p"},"python -m bats.__main__")),Object(o.b)("p",null,"There are four actions supported:"),Object(o.b)("pre",null,Object(o.b)("code",Object(r.a)({parentName:"pre"},{}),"Metadata : Reads a metadata.json file that contains the configuration of tests to execute\nCompare : Compares two files that are provided as command-line arguments\nExtract : Extracts a property from a file\n")),Object(o.b)("h2",{id:"params"},"Params:"),Object(o.b)("p",null,"Pass metadata.json"),Object(o.b)("pre",null,Object(o.b)("code",Object(r.a)({parentName:"pre"},{}),"$ python -m bats metadata metadata.json\n")),Object(o.b)("p",null,"Pass dynamic values - Pass dynamic values that will be replaced in the metadata.json.\nFor example if I execute below command,"),Object(o.b)("pre",null,Object(o.b)("code",Object(r.a)({parentName:"pre"},{}),"$ python -m bats metadata metadata.json -D key=value\n")),Object(o.b)("p",null,"Then, it will replace ${key} with 'value' in below metadata.json"),Object(o.b)("pre",null,Object(o.b)("code",Object(r.a)({parentName:"pre"},{}),'{\n    "name": "Demonstrate dynamic value"\n    "tests": [\n        {\n            "name": "Sample test",\n            "checks": [\n                {\n                    "name": "Sample check",\n                    "source": {\n                        "property": "${key}"\n                        "type": "..."\n                        "file": "..."\n                    }\n                    "target": {\n                        "property": "${key}"\n                        "type": "..."\n                        "file": "..."\n                    }\n                }\n            ]\n        }\n    ]\n}\n')),Object(o.b)("p",null,"Fail on errors"),Object(o.b)("pre",null,Object(o.b)("code",Object(r.a)({parentName:"pre"},{}),"$ python -m bats metadata metadata.json --failon MISSING_PROPERTY\n")))}s.isMDXComponent=!0},134:function(e,t,n){"use strict";n.d(t,"a",(function(){return u})),n.d(t,"b",(function(){return d}));var r=n(0),a=n.n(r);function o(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function c(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function i(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?c(Object(n),!0).forEach((function(t){o(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):c(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function p(e,t){if(null==e)return{};var n,r,a=function(e,t){if(null==e)return{};var n,r,a={},o=Object.keys(e);for(r=0;r<o.length;r++)n=o[r],t.indexOf(n)>=0||(a[n]=e[n]);return a}(e,t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(r=0;r<o.length;r++)n=o[r],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(a[n]=e[n])}return a}var l=a.a.createContext({}),s=function(e){var t=a.a.useContext(l),n=t;return e&&(n="function"==typeof e?e(t):i(i({},t),e)),n},u=function(e){var t=s(e.components);return a.a.createElement(l.Provider,{value:t},e.children)},b={inlineCode:"code",wrapper:function(e){var t=e.children;return a.a.createElement(a.a.Fragment,{},t)}},m=a.a.forwardRef((function(e,t){var n=e.components,r=e.mdxType,o=e.originalType,c=e.parentName,l=p(e,["components","mdxType","originalType","parentName"]),u=s(n),m=r,d=u["".concat(c,".").concat(m)]||u[m]||b[m]||o;return n?a.a.createElement(d,i(i({ref:t},l),{},{components:n})):a.a.createElement(d,i({ref:t},l))}));function d(e,t){var n=arguments,r=t&&t.mdxType;if("string"==typeof e||r){var o=n.length,c=new Array(o);c[0]=m;var i={};for(var p in t)hasOwnProperty.call(t,p)&&(i[p]=t[p]);i.originalType=e,i.mdxType="string"==typeof e?e:r,c[1]=i;for(var l=2;l<o;l++)c[l]=n[l];return a.a.createElement.apply(null,c)}return a.a.createElement.apply(null,n)}m.displayName="MDXCreateElement"}}]);
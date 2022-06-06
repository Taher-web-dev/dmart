# DMART Svelte Frontend

This is a rudimentary desktop web frontend for DMART member experience (logged-in users' UI). 



### Technology stack and major libraries used.

Name | Version | Description
--- | --- | ---
**Svelte** | 3.x | Reactive JS Compiler
**Routify** | 2.x | File-based routing library for Svelte
**Bootstrap** | 5.x | CSS Framework. Used via Sveltestrap
**Rollup** | 2.x | Web resources build/bundle tool
**Svelte-i18n** | 3.x | Internationalization for svelte based on formatjs
**Javascript** | >= ES6 | Browser (client-side) programming language. (Typescript is not used)


### Running

```bash
# Install npm packages
npm install

# Dev mode (SPA on port 5000)
npm run dev

# Dev mode (SPA on port 5000 and SSR on port 5005)
npm run rollup
```

### Building productoin bundle
```bash
npm run build

# Preview the build
npm run serve
```


### Backend api / Space configuration

The active Backend api / space configuration can be set under `src/space_config/index.js`

# Frontend Architecture
- [Overview](#overview)
- [Technology Stack](#technology-stack)
  - [Svelte Basics](#svelte-basics)
  - [TailwindCSS Basics](#tailwindcss-basics)
  - [Flowbite Basics](#flowbite-basics)
- [Static Rendering with adapter-static](#static-rendering-with-adapter-static)
- [Project Structure](#project-structure)
  - [Core Organization](#core-organization)
  - [Routing Architecture](#routing-architecture)
  - [Internationalization](#internationalization)
- [Component Architecture](#component-architecture)
  - [Reusable UI Components](#reusable-ui-components)
  - [Layout Components](#layout-components)
  - [Component Composition Patterns](#component-composition-patterns)
  - [Building New Features](#building-new-features)
- [State Management](#state-management)
  - [Svelte Stores](#svelte-stores)
  - [API Communication](#api-communication)
- [Authentication and Authorization](#authentication-and-authorization)
- [Styling Architecture](#styling-architecture)
  - [TailwindCSS Integration](#tailwindcss-integration)
  - [Flowbite Components](#flowbite-components)
- [Development Workflow](#development-workflow)
  - [Local Development](#local-development)
  - [Build Process](#build-process)
  - [Testing](#testing)

This document details the frontend architecture of the MKCentral application, covering the technology choices, code organization, and implementation patterns.

## Overview

Our frontend is a dynamic, multi-language web application built using modern web technologies. It's designed as a single-page application with a component-based architecture that provides a responsive user interface for managing tournaments, player registrations, team management, and other Mario Kart community activities.

The application is statically generated at build time while still supporting dynamic interactions through client-side JavaScript, providing a balance between performance and user experience.

## Technology Stack

We've built our frontend using the following core technologies:

- **[Svelte](https://svelte.dev/)** - A modern JavaScript framework that compiles components at build time for efficient runtime execution
- **[SvelteKit](https://kit.svelte.dev/)** - Svelte's official application framework for building server-rendered, statically generated, or hybrid web applications
- **[TypeScript](https://www.typescriptlang.org/)** - A strongly typed programming language that builds on JavaScript
- **[TailwindCSS](https://tailwindcss.com/)** - A utility-first CSS framework for rapidly building custom designs
- **[Flowbite](https://flowbite.com/)** - A component library built on top of TailwindCSS
- **[typesafe-i18n](https://github.com/ivanhofer/typesafe-i18n)** - A fully type-safe internationalization library for JavaScript/TypeScript projects

### Svelte Basics

Svelte is a compiler-based JavaScript framework that converts components into efficient vanilla JavaScript at build time. Here are the essential concepts:

#### Component Structure

A Svelte component is a `.svelte` file with three sections:
- `<script>` - JavaScript logic
- `<style>` - Scoped CSS styles
- HTML markup for the UI

```html
<script>
  let count = 0;
  function increment() { count++; }
</script>

<button on:click={increment}>Count: {count}</button>

<style>
  button { background: #ff3e00; color: white; }
</style>
```

#### Key Svelte Features

- **Reactivity**: Variables automatically update the UI when changed
- **Directives**: Special element attributes like `on:click`, `bind:value`, etc.
- **Control Flow**: `{#if}`, `{#each}`, `{#await}` blocks for templating
- **Props**: Use `export let propName` to define component properties
- **Events**: Components can dispatch custom events with `createEventDispatcher`

For a complete guide, see the [Svelte tutorial](https://svelte.dev/tutorial/basics).

### TailwindCSS Basics

TailwindCSS is a utility-first CSS framework that allows you to build designs directly in your markup using predefined utility classes.

```html
<!-- TailwindCSS example -->
<div class="p-4 rounded shadow bg-white">
  <h2 class="text-xl font-bold text-gray-800">Title</h2>
  <p class="text-gray-600 mt-2">Content goes here</p>
  <button class="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    Action
  </button>
</div>
```

**Common Utility Categories**:
- **Layout**: `flex`, `grid`, `container`
- **Spacing**: `p-4` (padding), `m-2` (margin)
- **Typography**: `text-lg`, `font-bold`
- **Colors**: `text-blue-600`, `bg-gray-200`
- **Responsive Design**: `md:flex`, `lg:text-xl`

For details, see the [TailwindCSS documentation](https://tailwindcss.com/docs).

### Flowbite Basics

Flowbite-Svelte provides pre-built components that integrate with TailwindCSS. Here's how to use them:

```html
<script>
  import { Button, Modal } from 'flowbite-svelte';
  let showModal = false;
</script>

<!-- Basic component usage -->
<Button color="blue" on:click={() => showModal = true}>Open Modal</Button>

<!-- Components can be customized with props and additional classes -->
<Modal bind:open={showModal} title="Information" class="w-full max-w-md">
  <p>Content goes here</p>
  <svelte:fragment slot="footer">
    <Button color="gray" on:click={() => showModal = false}>Close</Button>
  </svelte:fragment>
</Modal>
```

For the complete component library, see the [Flowbite-Svelte documentation](https://flowbite-svelte.com/).

## Static Rendering with adapter-static

We use SvelteKit's `adapter-static` with `prerender = true` to generate a fully static multi-page website at build time. This is a crucial aspect of our architecture that affects how code is structured and executed.

### How Static Rendering Works

1. **Build-Time Pre-rendering**: When running `npm run build`, SvelteKit generates separate static HTML files for every route in the application.
2. **Multi-Page Structure**: Unlike a single-page application (SPA), each route is a separate HTML file with its own complete HTML document.
3. **Traditional Page Navigation**: Navigation between routes causes full page reloads rather than client-side routing.
4. **No Server Runtime**: There is no Node.js server running in production; all pages are served as static files.

### Important Implications

This approach has several important implications for development:

1. **Script Execution Timing**: 
   - Code in the top-level `<script>` tag runs during build time, not when a user visits the page
   - API calls or browser-specific code in the script section will run during the build, not in the browser

2. **Client-Side Code**:
   - Use `onMount` from Svelte for code that should run in the browser
   - Use client-side lifecycle functions for browser interactions, DOM manipulation, or API calls

3. **Common Patterns**:

```html
<!-- INCORRECT: Will only run during build -->
<script>
  const response = await fetch('/api/data'); // ⚠️ Runs at build time
  const data = await response.json();
</script>

<!-- CORRECT: Runs in the browser -->
<script>
  import { onMount } from 'svelte';
  let data = [];
  
  onMount(async () => {
    const response = await fetch('/api/data');
    data = await response.json();
  });
</script>
```

4. **Server vs. Client**:
   - Browser-specific objects like `window`, `document`, and `localStorage` are only available in client-side code
   - Be careful with conditional rendering that depends on browser APIs

### Page Structure and Navigation

When a user interacts with our site:

1. Each page is a complete, pre-rendered HTML document
2. JavaScript is included to handle dynamic content and interactivity within each page
3. Navigating to a different route loads an entirely new HTML file
4. State is not automatically preserved between pages
5. API requests are made independently from each page

Understanding this architecture is crucial for developing new features properly and avoiding common pitfalls related to static site generation and multi-page navigation.

## Project Structure

### Core Organization

Our frontend codebase follows a logical organization that separates concerns and promotes reusability:

- **Components**: Reusable UI elements are stored in `src/lib/components/`, organized by functionality (e.g., common UI elements, feature-specific components)
- **Routes**: Feature pages follow SvelteKit's file-based routing system in `src/routes/[lang]/` with each major section having its own directory
- **Stores**: State management is centralized in `src/lib/stores/` with Svelte's reactive stores
- **Types**: Type definitions are stored in `src/lib/types/` to ensure consistency across the codebase
- **Utils**: Helper functions and common logic reside in `src/lib/util/`
- **Translations**: Internationalization files are organized in `src/i18n/` by language code

When adding a new feature, you'll typically need to:

1. Create new components in `src/lib/components/` (or in a feature-specific subfolder)
2. Add new routes in `src/routes/[lang]/` using SvelteKit's file-based routing
3. Define any necessary types in `src/lib/types/`
4. Add translations for all UI text in `src/i18n/` for all supported languages
5. Create or update stores in `src/lib/stores/` if your feature requires state management

### Routing Architecture

We use SvelteKit's file-based routing system with a language parameter incorporated directly into the URL structure. Routes are organized into three main concepts:

1. **Language-based Routes**: All routes are nested under a `[lang]` parameter to support internationalization
2. **Section-based Organization**: Routes are grouped by application section (tournaments, registry, etc.)
3. **Dynamic Parameters**: Routes use SvelteKit's dynamic parameter syntax (e.g., `[tournamentId]`) for accessing specific resources

For example, a tournament details page would live at `/src/routes/[lang]/tournaments/[id]/+page.svelte`, which generates a URL like `/en-us/tournaments/123`.

#### Page and Layout Components

SvelteKit uses two special component types for routing:

1. **+page.svelte**: Contains the main content for a specific route. For example:
```html
<!-- /src/routes/[lang]/tournaments/[id]/+page.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import type { Tournament } from '$lib/types/tournament';
    
    let tournamentId: string;
    let tournament: Tournament | null = null;

    onMount(() => {
        tournamentId = $page.params.id;
        const response = await fetch(`/api/tournaments/${tournamentId}`);
        tournament = await response.json();
    });
</script>

<div class="tournament-details">
    {#if tournament}
        <h1>{tournament.name}</h1>
        <!-- Tournament content -->
    {:else}
        <p>Loading tournament details...</p>
    {/if}
</div>
```

2. **+layout.svelte**: Provides shared layout elements for a section of the application. Layouts wrap page components and can be nested. For example:
```html
<!-- /src/routes/[lang]/tournaments/+layout.svelte -->
<script lang="ts">
    import TournamentNavigation from '$lib/components/tournaments/TournamentNavigation.svelte';
</script>

<div class="tournament-section">
    <TournamentNavigation />
    
    <!-- This slot is filled by the matching +page.svelte -->
    <slot />
</div>
```

3. **+layout.ts**: Provides data at build time for statically rendered pages. It executes during the build process, not when a user visits the page. In our application, it's primarily used for:
   - Setting the active navigation item for proper highlighting in the navbar
   - Processing the language parameter for internationalization

Example from the codebase:
```typescript
// /src/routes/[lang]/tournaments/+layout.ts
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ params }) => {
    // This code runs during the build process, not in the browser
    
    // Determine the active navigation item for this route
    const activeNavItem = 'TOURNAMENTS';
    
    return {
        activeNavItem
    };
};
```

Key points about `+layout.ts` in our statically rendered site:
- It runs during the build process, not when users visit the site
- It cannot make dynamic API calls that would be different for each user
- It's useful for determining static properties like active navigation items, route validation, etc.
- Values returned are embedded in the static HTML and JavaScript bundle

#### Route Parameters and Query Parameters

The `$page` store provides access to route parameters and query parameters.

1. **Route Parameters**: Access URL parameters through the `$page.params` store:
```html
<script lang="ts">
    import { page } from '$app/stores';
    
    // For URL /en-us/tournaments:
    const lang = $page.params.lang; // 'en-us'
</script>
```

> **Important Note About Static Rendering**: Route parameters like `lang` are part of the file-based routing structure and are known at build time. This means they can be accessed in the top-level script without `onMount`, even in our statically rendered site. The actual values are determined during build time and embedded in the generated HTML and JavaScript.

2. **Query Parameters**: Access query string parameters through `$page.url.searchParams`:
```html
<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    
    // For URL /en-us/tournaments?filter=active
    let filter: string | null = null;
    
    onMount(() => {
        filter = $page.url.searchParams.get('filter');
    });
</script>
```

> **Query Parameters vs Route Parameters**: Unlike route parameters, query parameters are not known at build time and can only be accessed at runtime in the browser. This is why we must use `onMount` to access them, as they depend on the specific URL the user navigates to.

#### API Routes

We use a separate backend API rather than SvelteKit's server routes. All API calls should:

1. Use the `/api` prefix
2. Handle errors consistently
3. Follow RESTful patterns

Example API interaction:
```typescript
async function fetchTournament(id: string): Promise<Tournament> {
    const response = await fetch(`/api/tournaments/${id}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch tournament: ${response.status}`);
    }
    return await response.json();
}
```

### Internationalization

We use [typesafe-i18n](https://github.com/ivanhofer/typesafe-i18n) for internationalization with language codes included directly in the URL structure. For comprehensive details, refer to the dedicated [Internationalization Documentation](internationalization.md).

Basic usage in components:

```html
<script lang="ts">
  import LL from '$i18n/i18n-svelte';
</script>

<h1>{$LL.TOURNAMENTS.LIST_TITLE()}</h1>
<p>{$LL.TOURNAMENTS.DESCRIPTION()}</p>
```

The main language files are stored in `src/i18n/` and any new user-facing text should be added to all supported language files.

## Component Architecture

### Reusable UI Components

We've built a component-based architecture with several key reusable components that provide the foundation for our user interface:

```html
<!-- Section: Container for content blocks -->
<Section header="Tournament Details">
  <div slot="header_content">
    <Button href="/{$page.params.lang}/tournaments">Back</Button>
  </div>
  
  <!-- Content goes here -->
  <div class="player-info">
    <!-- Flag: Display country flags -->
    <Flag country_code="US" size="small" />
    
    <!-- Badges: Display status, tags, game info -->
    <TagBadge tag="MKC" color="#ff3e00" />
    <GameBadge game="mk8dx" />
    <ModeBadge mode="150cc" />
    
    <!-- Dialog: Modal dialog implementation -->
    <Button on:click={() => dialog.open()}>Options</Button>
    
    <!-- Dropdown: Menu with options -->
    <Dropdown>
      <DropdownItem on:click={handleEdit}>Edit</DropdownItem>
      <DropdownItem on:click={handleDelete}>Delete</DropdownItem>
    </Dropdown>
  </div>
</Section>

<!-- Dialog definition that would be referenced above -->
<Dialog bind:this={dialog} header="Options">
  <p>Select an action:</p>
  <div class="actions">
    <Button color="red">Delete</Button>
    <Button on:click={() => dialog.close()}>Cancel</Button>
  </div>
</Dialog>
```

These components provide consistent styling, behavior, and structure across our application. Some key components include:

- **Section**: Container with optional header and content slots
- **Button**: Consistent button styling with various color options
- **Badge** components: Visual indicators for tags, games, modes, etc.
- **Flag**: Country flag display with consistent sizing
- **Dialog**: Modal dialog implementation
- **Table**: Consistent tabular data display
- **Dropdown**: Menu with selectable options

Check the component folders in `src/lib/components/` for more reusable UI elements.

### Layout Components

We use several key layout components to structure content:

#### Table

The `Table` component provides consistent styling and structure for tabular data:

```html
<Table data={items} let:item>
  <colgroup slot="colgroup">
    <col class="name" />
    <col class="game" />
    <col class="status" />
  </colgroup>

  <tr slot="header">
    <th>{$LL.COMMON.NAME()}</th>
    <th>{$LL.COMMON.GAME()}</th>
    <th>{$LL.COMMON.STATUS()}</th>
  </tr>

  <tr>
    <td>{item.name}</td>
    <td><GameBadge game={item.game} /></td>
    <td>{item.status}</td>
  </tr>
</Table>
```

#### Dropdown

The `Dropdown` component provides a consistent dropdown/popover menu:

```html
<Button>
  {$LL.COMMON.ACTIONS()}
  <ChevronDownOutline class="w-3 h-3 ms-2" />
</Button>

<Dropdown>
  <DropdownItem href="/{$page.params.lang}/items/{item.id}/edit">
    {$LL.COMMON.EDIT()}
  </DropdownItem>
  <DropdownItem on:click={handleDelete}>
    {$LL.COMMON.DELETE()}
  </DropdownItem>
</Dropdown>
```

### Component Composition Patterns

We follow specific patterns for component composition that make it easy to build consistent user interfaces:

#### Slots for Flexible Content

In Svelte, a "slot" is a placeholder in a component where content can be inserted from the parent component. Slots allow components to be flexible containers that can receive and display different content while maintaining consistent structure and styling. The default unnamed slot receives any content passed directly to the component, while named slots allow content to be targeted to specific areas of the component.

The following example shows how a component (`MyComponent`) defines slots and how a parent component can fill those slots:

```html
<!-- MyComponent.svelte (Component definition) -->
<div class="container">
  <div class="header">
    <h2>{title}</h2>
    <slot name="header_actions" />
  </div>
  
  <div class="content">
    <slot />  <!-- This is the default/unnamed slot -->
  </div>
  
  <div class="footer">
    <slot name="footer" />
  </div>
</div>

<!-- Usage in a parent component -->
<MyComponent title="Example">
  <div slot="header_actions">
    <Button>Action</Button>
  </div>
  
  <p>Main content goes here</p>  <!-- This goes into the default slot -->
  
  <div slot="footer">
    Footer content
  </div>
</MyComponent>
```

This pattern allows components to maintain consistent structure while being flexible enough to display different content in different contexts.

#### Component Events

Components use Svelte's event system to communicate with parent components:

```html
<!-- Child component (ItemCard.svelte) -->
<script>
  import { createEventDispatcher } from 'svelte';
  
  export let item;
  const dispatch = createEventDispatcher();
  
  function handleEdit() {
    dispatch('edit', { id: item.id });
  }
  
  function handleDelete() {
    dispatch('delete', { id: item.id });
  }
</script>

<div class="item-card">
  <h3>{item.name}</h3>
  <div class="actions">
    <Button on:click={handleEdit}>Edit</Button>
    <Button on:click={handleDelete}>Delete</Button>
  </div>
</div>

<!-- Parent component usage -->
<ItemCard {item}
  on:edit={handleItemEdit}
  on:delete={handleItemDelete}
/>
```

#### Form Components

Our form components follow a consistent pattern:

```html
<script>
  export let item = null;
  const isNew = !item;
  let form = item ? { ...item } : { name: '', description: '' };
  
  async function handleSubmit() {
    try {
      const response = await fetch(
        isNew ? '/api/items' : `/api/items/${item.id}`, {
        method: isNew ? 'POST' : 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
      
      if (!response.ok) throw new Error('Submission failed');
      // Success handling...
    } catch (error) {
      // Error handling...
    }
  }
</script>

<form on:submit|preventDefault={handleSubmit}>
  <div class="form-field">
    <label for="name">{$LL.COMMON.NAME()}</label>
    <input id="name" bind:value={form.name} required />
  </div>
  
  <Button type="submit">
    {isNew ? $LL.COMMON.CREATE() : $LL.COMMON.SAVE()}
  </Button>
</form>
```

### Building New Features

When building a new feature for our application, follow these component-based patterns:

1. **Break down the UI** into reusable components with clear responsibilities
2. **Reuse existing components** whenever possible (Section, Table, Badge, Dialog, etc.)
3. **Create feature-specific components** for unique UI elements
4. **Organize by domain** in appropriate subdirectories (`tournaments/`, `registry/`, etc.)
5. **Use TypeScript interfaces** for component props and data structures
6. **Implement internationalization** for all user-facing text
7. **Handle permissions** by conditionally rendering UI elements based on user roles

Example structure:
```
src/
├── lib/components/tournaments/bracket/
│   ├── BracketView.svelte       # Main display
│   └── BracketNode.svelte       # Individual node
├── lib/types/bracket.ts         # Type definitions
└── routes/[lang]/tournaments/[id]/bracket/
    ├── +page.svelte             # View page
    └── edit/+page.svelte        # Edit page
```

## State Management

### Svelte Stores

Svelte stores are a mechanism for managing reactive state that can be shared across multiple components on a page. In our application, stores reset when navigating between pages due to our static site architecture.

```html
<script>
  // Import the user store
  import { user } from '$lib/stores/stores';
  
  // Access the store with $ prefix for automatic reactivity
  function isAdmin() {
    return $user.permissions.includes('admin');
  }
</script>

<!-- The UI automatically reacts when store values change -->
{#if $user.id}
  <p>Welcome, {$user.player?.name}!</p>
  
  {#if isAdmin()}
    <AdminPanel />
  {/if}
{:else}
  <p>Please log in</p>
{/if}
```

Our main stores include:
- `user`: Contains authentication state, user info, and permissions
- `have_unread_notification`: Tracks unread notification count

For more advanced usage, see the [Svelte store documentation](https://svelte.dev/tutorial/writable-stores).

### API Communication

Our frontend communicates with the backend API using the following patterns:

```typescript
// Example API function with error handling
async function fetchData(id: string): Promise<ItemType | null> {
  try {
    const response = await fetch(`/api/items/${id}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    notify.error($LL.ERRORS.FETCH_FAILED());
    console.error(error);
    return null;
  }
}
```

Best practices:
- Use TypeScript interfaces for request and response data
- Implement consistent error handling with user feedback
- Handle loading states in the UI
- Make API calls in `onMount` or event handlers, not top-level script sections

## Authentication and Authorization

We implement the authentication and authorization system described in detail in the [Authentication & Authorization](auth.md) documentation. Here's what you need to know for frontend development:

```html
<!-- Conditional rendering based on permissions -->
{#if check_permission($user, permissions.manage_users)}
  <UserManagement />
{/if}

<!-- Access control for team features -->
{#if check_team_permission($user, team_permissions.edit_team, teamId)}
  <EditTeamButton {teamId} />
{/if}
```

Best practices:
- Frontend permission checks are for UI purposes only (backend validation is still required)
- Use the appropriate permission checker for the context (global, team, tournament, or series)
- Always handle the unauthorized state gracefully in the UI

## Styling Architecture

### TailwindCSS Integration

We use TailwindCSS for styling with a utility-first approach. Our configuration is in `tailwind.config.cjs` with custom colors and components.

Best practices:
- Use utility classes directly in component markup
- Follow our established color scheme
- Use responsive utilities (`md:`, `lg:`, etc.) for different screen sizes
- Only add custom CSS when necessary

### Flowbite Components

We use Flowbite-Svelte components as building blocks for our UI. These components integrate with TailwindCSS and can be customized with additional classes.

```html
<!-- Example Flowbite component with customization -->
<Button color="primary" class="my-4 shadow-lg">Action</Button>
<Card padding="lg" class="border border-gray-300">
  <h3 class="text-xl mb-2">Card Title</h3>
  <p>Card content</p>
</Card>
```

For available components, see the [Flowbite-Svelte documentation](https://flowbite-svelte.com/).

## Development Workflow

### Local Development

Our development environment uses Docker containers and is set up using VS Code's Dev Containers. As described in the [Onboarding Guide](onboarding.md), the system is comprised of multiple containers:

1. **Development Container**: Contains all the tools and extensions needed for development
2. **API Container**: Runs the Python Starlette backend API
3. **Frontend Container**: Runs the Svelte frontend development server
4. **CF Worker Container**: Routes requests to either the API or Frontend based on URL patterns

To start development:

1. Open the project in VS Code with the Remote-Containers extension
2. Open the `MarioKartCentral.code-workspace` workspace file
3. Access the application at http://localhost:5001
4. Frontend URLs follow the pattern `localhost:5001/[lang]/...`
5. API endpoints are accessed via `localhost:5001/api/...`

The development environment features hot reloading for both the frontend and backend, meaning code changes are automatically applied without needing to restart the services manually.

For debugging the frontend, since Svelte doesn't have integrated debugging with VS Code, you can:
- Use `console.log()` statements for quick debugging
- Add a `debugger;` statement in your code to trigger browser dev tools
- Use the browser's development tools to inspect components and state

### Build Process

Our production build process:

1. Generates separate static HTML files for every route and language using `adapter-static`
2. Optimizes and bundles JavaScript and CSS
3. Processes assets for optimal delivery
4. Outputs to the `build` directory

The build is triggered with:
```bash
npm run build
```

For details about adding new localizations:
1. Add your new locale to `/src/frontend/src/i18n/`
2. Run `npx typesafe-i18n` inside the `/src/frontend` folder to regenerate type files
3. Update the routes configuration if needed

### Testing

Currently, we don't have automated testing set up for the frontend. Testing is primarily done manually by:

1. Testing changes locally in different browsers
2. Testing features across different language settings
3. Verifying UI responsiveness across different screen sizes
4. Manual verification of feature functionality

For comprehensive information about our entire application architecture, see the [Architecture Overview](architecture.md).
# Internationalization (i18n)

This document explains the internationalization system used in Mario Kart Central and provides guidance for developers working with translations.

## Table of Contents
- [Supported Languages](#supported-languages)
- [Implementation Architecture](#implementation-architecture)
- [Frontend Translation System](#frontend-translation-system)
  - [Translation Files Structure](#translation-files-structure)
  - [Auto-Generated Files](#auto-generated-files)
  - [Base Language Structure](#base-language-structure)
  - [Type Safety Features](#type-safety-features)
  - [Custom Types](#custom-types)
- [URL Structure and Language Detection](#url-structure-and-language-detection)
  - [Language in URL Path](#language-in-url-path)
  - [Language Detection Process](#language-detection-process)
- [Working with Translations](#working-with-translations)
  - [Adding New Translatable Strings](#adding-new-translatable-strings)
  - [Simple Strings](#simple-strings)
  - [Strings with Variables](#strings-with-variables)
  - [Strings with Pluralization](#strings-with-pluralization)
  - [Using Formatters](#using-formatters)
  - [Similar Languages and Translation Inheritance](#similar-languages-and-translation-inheritance)
- [Translation Workflow](#translation-workflow)
- [Translation Guidelines](#translation-guidelines)
- [User Language Preferences](#user-language-preferences)
- [Testing](#testing)

## Supported Languages
The application currently supports these languages:
- English (United States) - `en-us` (base language)
- English (Great Britain) - `en-gb` 
- German - `de`
- Spanish - `es`
- French - `fr`
- Japanese - `ja`

## Implementation Architecture
The i18n system consists of these main components:
1. **Frontend translations** using the typesafe-i18n package
2. **URL-based language paths** (e.g., `/en-us/tournaments`)
3. **Language detection and routing** via Cloudflare Worker
4. **Language preference storage** in browser cookies

## Frontend Translation System
MarioKartCentral uses [typesafe-i18n](https://github.com/ivanhofer/typesafe-i18n) for type-safe translations in the frontend. This library provides strong type checking to prevent common i18n mistakes and ensures all translations have the required parameters.

### Translation Files Structure
Translation files are organized under `/src/frontend/src/i18n/` with each language having its own directory:
```
/src/frontend/src/i18n/
├── i18n-util.ts           # Auto-generated utility functions
├── i18n-types.ts          # Auto-generated type definitions
├── i18n-svelte.ts         # Auto-generated Svelte bindings
├── i18n-util.sync.ts      # Auto-generated synchronous loading utilities
├── i18n-util.async.ts     # Auto-generated asynchronous loading utilities
├── formatters.ts          # Custom formatters (manually created)
├── custom-types.ts        # Custom type definitions (manually created)
├── en-us/                 # Base language translations (manually created)
│   └── index.ts
├── de/                    # German translations (manually created)
│   └── index.ts
└── [other language folders]
```

### Auto-Generated Files
When you run `npx typesafe-i18n` in the `/src/frontend` directory, the following files are automatically generated:
- `i18n-types.ts` - TypeScript type definitions for all translations
- `i18n-util.ts` - Core utility functions for using translations
- `i18n-util.sync.ts` - Utilities for synchronous loading of translations
- `i18n-util.async.ts` - Utilities for asynchronous loading of translations
- `i18n-svelte.ts` - Svelte-specific bindings and stores

These files should **never be manually edited** as they will be overwritten when regenerating types.

The only files you should manually edit are:
- Language translation files in language directories (`en-us/index.ts`, etc.)
- `formatters.ts` (if adding custom formatters)
- `custom-types.ts` (if needed for additional type customization)

### Base Language Structure
The base language (`en-us`) defines the translation structure that all other languages must follow:
```typescript
// Example from /src/frontend/src/i18n/en-us/index.ts
const en_us: BaseTranslation = {
  LANGUAGE: 'American English',
  COLORS: {
    RED_1: 'Red 1',
    // other color translations
  },
  COMMON: {
    GAME: 'Game',
    // other common translations
  },
  // other translation sections
};
```

The system generates TypeScript typings from this structure to ensure type safety throughout the application. These types enforce that all languages include the same keys and structure.

### Type Safety Features
The typesafe-i18n library provides several type checking features:
- Auto-completion for all defined locales and translation keys
- Compile-time errors if you forget to pass required arguments
- Errors if you pass the wrong type of arguments
- Errors if translations are missing in non-base languages
- Ensuring all translations include the necessary placeholders

### Custom Types
The `custom-types.ts` file allows you to define custom TypeScript types for parameters used in translations. This is particularly useful when you need to:
1. **Define parameter types for translation functions** - When your translations expect specifically typed parameters
2. **Create type definitions for formatters** - When your formatters require specific parameter shapes
3. **Extend the base translation type** - When you need to add additional properties or functionality

#### How It Works
When you use a custom type in a translation string with a formatter, you need to define that type in `custom-types.ts`:
```typescript
// In a translation file
const en: BaseTranslation = {
  PLAYER_SCORE: 'Player {name} scored {score:PlayerScore|formatScore}'
}
// In custom-types.ts
// This type will be used by the formatter
export type PlayerScore = {
  points: number
  rank: number
  isPersonalBest: boolean
}
```

Then your formatter can safely use the properties of that type:
```typescript
// In formatters.ts
const formatScore = (score: PlayerScore): string => {
  let result = `${score.points} points (Rank: ${score.rank})`;
  if (score.isPersonalBest) {
    result += ' 🏆 Personal Best!';
  }
  return result;
}
```

## URL Structure and Language Detection
### Language in URL Path
All site URLs include the language code as the first path segment:
```
https://mariokartcentral.com/en-us/tournaments
https://mariokartcentral.com/fr/players
```

This pattern provides:
- Clear indication of current language in the URL
- Proper indexing of translated content by search engines
- Support for direct sharing of content in specific languages

### Language Detection Process
The Cloudflare Worker ([`/src/cf-worker/src/index.ts`](/src/cf-worker/src/index.ts)) handles language detection and redirection through this flow:
1. If the URL already has a valid language segment (`/en-us/`, `/fr/`, etc.), verify if it matches user preference:
   - If it doesn't match the user's cookie preference, redirect to preferred language
   - Otherwise, serve content in the requested language
2. If the URL has no language segment:
   - Check for a `language` cookie
   - If no cookie exists, examine the `Accept-Language` header
   - Redirect to the appropriate language version (`/en-us/tournaments`, etc.)
3. Non-frontend routes bypass language detection:
   - API endpoints (e.g., `/api/...`)
   - Static resources 
   - Documentation routes

For detailed implementation, see the `handleFrontend` function in the Cloudflare Worker code.

## Working with Translations

### Adding New Translatable Strings
#### Simple Strings
When adding new text that needs to be translated in the application, follow these steps:
1. **Add the string to the base language file first**:
   ```typescript
   // In /src/frontend/src/i18n/en-us/index.ts
   const en_us: BaseTranslation = {
     // ...existing translations
     
     // Add your new string
     TOURNAMENTS: {
       // ...existing tournament translations
       NEW_FEATURE: 'New tournament feature',
       REGISTRATION_CLOSED: 'Registration is now closed'
     }
   };
   ```
2. **Generate the updated type definitions**:
   ```bash
   cd /src/frontend
   npx typesafe-i18n
   ```
   > **Note**: After running the generator, TypeScript will show errors in all other language files 
   > that are missing the new translations. This is an intentional feature that helps ensure you don't 
   > forget to translate content in any language.
3. **Add the translations to all other language files**:
   ```typescript
   // In /src/frontend/src/i18n/fr/index.ts
   const fr: Translation = {
     // ...existing translations
     
     // Add your translated strings
     TOURNAMENTS: {
       // ...existing tournament translations
       NEW_FEATURE: 'Nouvelle fonctionnalité de tournoi',
       REGISTRATION_CLOSED: 'Les inscriptions sont maintenant fermées'
     }
   };
   ```
4. **Use the translation in your component**:
   ```typescript
   // In a Svelte component
   import LL from '../i18n/i18n-svelte';
   
   // Then in your template:
   // {$LL.TOURNAMENTS.NEW_FEATURE()}
   ```

#### Strings with Variables
For strings that include dynamic values:
1. **Add the parameterized string to the base language**:
   ```typescript
   // In /src/frontend/src/i18n/en-us/index.ts
   const en_us: BaseTranslation = {
     // ...existing translations
     
     TOURNAMENTS: {
       // ...existing tournament translations
       PLAYER_COUNT: '{count:number} players registered'
     }
   };
   ```
2. **Generate type definitions and add to other languages**:
   ```typescript
   // In /src/frontend/src/i18n/fr/index.ts
   const fr: Translation = {
     // ...existing translations
     
     TOURNAMENTS: {
       // ...existing tournament translations
       PLAYER_COUNT: '{count:number} joueurs inscrits'
     }
   };
   ```
3. **Use with parameters**:
   ```typescript
   // In your component
   const registeredPlayers = 42;
   
   // {$LL.TOURNAMENTS.PLAYER_COUNT({ count: registeredPlayers })}
   ```

#### Strings with Pluralization
For strings that change based on count and different languages have different pluralization rules:
1. **Add pluralized string to base language**:
   ```typescript
   // In /src/frontend/src/i18n/en-us/index.ts
   const en_us: BaseTranslation = {
     // ...existing translations
     
     TOURNAMENTS: {
       // ...existing tournament translations
       DAY_REMAINING: '{count:number} {{day|days}} remaining'
     }
   };
   ```
2. **Add to other languages with appropriate pluralization rules**:
   ```typescript
   // In /src/frontend/src/i18n/fr/index.ts
   const fr: Translation = {
     // ...existing translations
     
     TOURNAMENTS: {
       // ...existing tournament translations
       DAY_REMAINING: '{count:number} {{jour|jours}} restant'
     }
   };
   
   // In /src/frontend/src/i18n/ja/index.ts
   const ja: Translation = {
     // ...existing translations
     
     TOURNAMENTS: {
       // ...existing tournament translations
       DAY_REMAINING: 'あと{count:number}日' // Japanese doesn't use plural forms
     }
   };
   ```
3. **Use with counts**:
   ```typescript
   // In your component
   const daysLeft = 1;
   
   // For 1 in English: {$LL.TOURNAMENTS.DAY_REMAINING({ count: daysLeft })}
   // Output: "1 day remaining"
   
   // For 1 in French: {$LL.TOURNAMENTS.DAY_REMAINING({ count: daysLeft })}
   // Output: "1 jour restant"
   
   // For 1 in Japanese: {$LL.TOURNAMENTS.DAY_REMAINING({ count: daysLeft })}
   // Output: "あと1日"
   
   const daysLeft = 5;
   // For 5 in English: {$LL.TOURNAMENTS.DAY_REMAINING({ count: daysLeft })}
   // Output: "5 days remaining"
   
   // For 5 in French: {$LL.TOURNAMENTS.DAY_REMAINING({ count: daysLeft })}
   // Output: "5 jours restant"
   
   // For 5 in Japanese: {$LL.TOURNAMENTS.DAY_REMAINING({ count: daysLeft })}
   // Output: "あと5日" (unchanged from singular)
   ```

### Using Formatters
Formatters allow you to transform values before they are inserted into translations. They are defined in the `formatters.ts` file:
```typescript
// src/frontend/src/i18n/formatters.ts
import type { FormattersInitializer } from 'typesafe-i18n'
import type { Locales, Formatters } from './i18n-types'
export const initFormatters: FormattersInitializer<Locales, Formatters> = (locale: Locales) => {
  const formatters: Formatters = {
    // Custom formatters for your application
    ordinalSuffix: (value: number): string => {
      // Format logic here...
      return `${value}${suffix}`
    },
    
    // Date formatter example
    date: (date: Date): string => {
      return new Intl.DateTimeFormat(locale).format(date);
    }
  }
  return formatters
}
```

To use formatters in translations:
```typescript
// In translation file
const en_us: BaseTranslation = {
  // Simple formatter usage
  TOURNAMENT_DATE: 'Tournament date: {date|date}',
  
  // Formatter with type
  PLAYER_SCORE: 'Player {name} scored {score:PlayerScore|formatScore}'
}
// In component
const tournamentDate = new Date();
// {$LL.TOURNAMENT_DATE({ date: tournamentDate })}
// Output: "Tournament date: 5/23/2023"
```

### Similar Languages and Translation Inheritance
For languages with only slight differences (like `en-us` and `en-gb`), you can extend one from another using the `extendDictionary` utility:
```typescript
// src/frontend/src/i18n/en-gb/index.ts
import type { Translation } from '../i18n-types';
import en_us from '../en-us';
import { extendDictionary } from '../i18n-util';
const en_gb = extendDictionary(en_us, {
  // Override only what differs
  COLORS: {
    GREY_1: 'Grey 1',  // Instead of "Gray 1" in en-us
    // Other overrides
  }
});
export default en_gb;
```

This approach is useful for minimizing duplication between similar languages while still ensuring type safety.

## Translation Workflow
When working with translations in the MarioKartCentral project:
1. **Always update the base language first** - The `en-us` locale defines the structure for all other languages
2. **Run the generator after any changes** - Run `npx typesafe-i18n` to regenerate type definitions
3. **CI/CD integration** - When running in CI environments, use `npx typesafe-i18n --no-watch` to generate types once without watching for changes
4. **Type checking** - TypeScript will notify you of missing or incorrect translations

## Translation Guidelines
When translating content:
1. **Keep variable placeholders intact** - Don't modify text within curly braces:
   - Example: `"Hello {player_name}"` → `"Bonjour {player_name}"`
2. **Maintain formatters** - Don't change formatter references:
   - Example: `{count|ordinalSuffix}` should remain unchanged
3. **Preserve pluralization syntax**:
   - Example: `"{count:number} {{player|players}}"` should maintain the double-brace structure
4. **Follow existing style** - Match the tone and terminology of existing translations

## User Language Preferences
The system manages user language preferences through several mechanisms:
- Users can change language via the language picker in the navigation bar
- Selection sets a `language` cookie with 90-day expiration
- The Cloudflare Worker handles redirecting users to their preferred language on subsequent visits
- Users without a cookie are detected through their browser's `Accept-Language` header

## Testing
Before submitting translations:
1. Run the application locally with the new language
2. Navigate through all pages to ensure translations are displaying correctly
3. Test with different screen sizes to verify layout accommodates translated text
4. Verify that the language detection and URL handling work correctly
5. Test both synchronous and asynchronous loading of translations

For additional information on working with the frontend code, see [Architecture Overview: Frontend](architecture.md#frontend).
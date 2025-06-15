# Time Trials Feature Documentation

**Last Updated:** June 15, 2025  
**Status:** Core Features Implemented - Working Submission, Validation, and Adv#### Routes Structure
- `/time-trials` - Main time trials page with game selection
- `/time-trials/submit` - Time trial submission form with proof handling
- `/time-trials/[game]` - Game-specific track selection page
- `/time-trials/[game]/leaderboard` - **NEW**: Advanced leaderboard with comprehensive filtering and URL sharing
- `/time-trials/[game]/validation` - Staff proof validation queue interfaceLeaderboards

## Overview

The Time Trials feature allows players to submit and validate Mario Kart time trial records. The system supports multiple games (currently focused on Mario Kart World), provides a comprehensive proof validation workflow, and maintains advanced leaderboards with filtering capabilities. The feature has evolved significantly with working core functionality and a polished leaderboard experience.

## Architecture Overview

The time trials feature follows the established MKCentral architecture pattern:

- **Backend API:** Starlette-based REST endpoints at `/api/time-trials/*`
- **Database:** Hybrid storage with DuckDB for time trial data and SQLite for player information
- **Frontend:** Svelte-based interface for submission and viewing
- **Permissions:** Role-based access control for submission and validation

## Database Schema

### Core Tables (DuckDB)

#### `time_trials`
Primary table storing time trial records with embedded proofs:
```sql
CREATE TABLE time_trials (
    id VARCHAR PRIMARY KEY,           -- UUID
    version INTEGER NOT NULL,         -- Optimistic locking version
    player_id VARCHAR NOT NULL,       -- FK to SQLite players table
    game VARCHAR NOT NULL,            -- Game identifier (e.g., "mkworld")
    track VARCHAR NOT NULL,           -- Track abbreviation
    time_ms INTEGER NOT NULL,         -- Time in milliseconds
    data JSON NOT NULL,               -- Game-specific structured data
    description TEXT,                 -- Optional description
    proofs JSON NOT NULL DEFAULT '[]', -- Embedded proofs array with validation status
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

**Indexes:**
- `idx_time_trials_track` on `track`
- `idx_time_trials_player_id` on `player_id`
- `idx_time_trials_time_ms` on `time_ms`
- `idx_time_trials_game_track` on `(game, track)`

#### Embedded Proof Structure
Each proof in the `proofs` JSON array contains:
```json
{
    "id": "uuid",
    "url": "proof_url",
    "type": "screenshot|video|replay_file",
    "properties": ["time", "character", "kart"],
    "created_at": "2025-06-13T...",
    "validations": {
        "time": {
            "id": "validation_uuid",
            "is_valid": true,
            "notes": "Validation notes",
            "validated_at": "2025-06-13T...",
            "staff_id": "validator_player_id"
        }
    }
}
```

## Data Models

### Game-Specific Schemas

Time trial data is stored as JSON in the `data` field with type safety provided through Python dataclasses:

#### Base Schema (`TimeTrialData`)
```python
@dataclass
class TimeTrialData:
    lap_times: Optional[List[int]] = None
    character: Optional[str] = None
    kart: Optional[str] = None
```

#### Mario Kart 8 Deluxe (`MK8DXTimeTrialData`)
```python
@dataclass  
class MK8DXTimeTrialData(TimeTrialData):
    tires: Optional[str] = None
    glider: Optional[str] = None
    cc: Optional[int] = None
```

#### Mario Kart World (`MKWorldTimeTrialData`)
```python
@dataclass
class MKWorldTimeTrialData(TimeTrialData):
    # Currently no additional properties
    pass
```

## Backend Implementation

### Core Commands

Located in `/src/backend/common/data/commands/time_trials/`:

#### `CreateTimeTrialCommand`
- Validates input data and creates time trial with embedded proofs
- Handles game-specific data validation using schemas
- Returns `TimeTrial` object with embedded proofs

#### `ListTimeTrialsCommand`  
- Supports filtering by player, game, track, cc
- Joins DuckDB time trials with SQLite player data using ATTACH
- Returns `List[Tuple[TimeTrial, Optional[str], Optional[str]]]` (time_trial, player_name, player_country)

#### `ValidateProofPropertyCommand`
- Validates specific properties of submitted proofs within embedded structure
- Updates validation status directly in the proof's JSON structure
- Creates/updates validation records within the proof object

#### `ListProofsForValidationCommand`
- Returns all proofs requiring validation from embedded proof arrays
- Processes validation status from embedded JSON structure
- Used by staff validation interface

### API Endpoints

Located in `/src/backend/api/endpoints/time_trials.py`:

- `POST /api/time-trials/create` - Submit new time trial
- `GET /api/time-trials/list` - List time trials with filtering (enhanced with validation_status computation)
- `GET /api/time-trials/{trial_id}` - Get specific time trial
- `DELETE /api/time-trials/{trial_id}/delete` - Delete time trial
- `POST /api/time-trials/proofs/{proof_id}/properties/{property}/validate` - Validate proof property
- `GET /api/time-trials/proofs/validation-queue` - List proofs for validation

#### Enhanced Validation Status Logic
The `/api/time-trials/list` endpoint now includes computed `validation_status` field:
- **"validated"**: Records with proofs that validate both `track` and `time_ms`/`time` properties
- **"unvalidated"**: Records with proofs that don't validate both required properties
- **"proofless"**: Records without any proof submissions

## Frontend Implementation

### Current State

The frontend implementation now has **comprehensive core functionality** with a polished user experience:

#### Routes Structure
- `/time-trials` - Main time trials page with game selection
- `/time-trials/submit` - Time trial submission form with proof handling
- `/time-trials/[game]` - Game-specific track selection page
- `/time-trials/[game]/leaderboard` - **Advanced leaderboard with comprehensive filtering**
- `/time-trials/[game]/validation` - Staff proof validation queue interface

#### Key Components

##### Advanced Leaderboard (`/[game]/leaderboard/+page.svelte`) - **FULLY IMPLEMENTED**
- **Multi-filter system**: Track selection, country filtering, validation status options
- **Smart validation filtering**: 
  - "Show times pending validation" (unvalidated records)
  - "Show times without proof" (proofless records)  
  - Defaults to showing only validated records
- **Player deduplication**: Shows only each player's fastest time per track
- **Platform-specific proof icons**: YouTube, Twitch, X/Twitter, Screenshot, and Video icons
- **Clickable proof links**: Direct access to proof media
- **Internationalized country names**: Full country names instead of codes
- **URL synchronization**: Shareable links with all filter states preserved
- **Responsive design**: Adaptive layout for mobile and desktop
- **Real-time filtering**: Client-side filtering with instant results
- **Validation status badges**: Clear indicators for pending and missing proofs

##### Staff Validation Interface (`/[game]/validation/+page.svelte`)
- **Basic proof queue management** filtered by game
- **Individual property validation** with approve/reject actions
- **Validation status tracking** with timestamps and validator information
- **Notes support** for validation decisions
- **Permission-based access control**

##### Submission Form (`/submit/+page.svelte`)
- **Multi-proof submission** with URL and type selection
- **Game and track selection** with abbreviation handling
- **Time input validation** with format checking
- **Engine class selection** for supported games
- **Error handling and success feedback**

#### Frontend Features

1. **Complete Core UI:** All essential time trials functionality has polished interfaces
2. **Advanced Leaderboard System:** Comprehensive filtering, URL sharing, and validation status management
3. **Permission Integration:** Role-based access throughout implemented interfaces
4. **Responsive Design:** Mobile-friendly layouts across all pages
5. **Comprehensive Error Handling:** Robust error states and user feedback
6. **Full Type Safety:** Complete TypeScript integration with backend models
7. **Complete Internationalization:** i18n support throughout with localized country names
8. **Rich Media Handling:** Platform-specific proof icons with direct linking
9. **URL State Management:** Shareable and bookmarkable leaderboard configurations
10. **Real-time Validation Status:** Live proof status tracking and filtering

### Current Implementation Quality

The frontend now represents a **production-ready implementation** with:

1. **Game Focus:** Optimized for Mario Kart World with extensible architecture
2. **Complete Leaderboard Experience:** Advanced filtering and sharing capabilities  
3. **Polished UI/UX:** Professional-grade interface with proper accessibility
4. **Performance Optimized:** Client-side filtering and efficient data handling

## Permissions

The system uses role-based permissions:

- `SUBMIT_TIME_TRIAL` - Required to submit time trials
- `VALIDATE_TIME_TRIAL_PROOF` - Required for staff to validate proofs  
- `DELETE_TIME_TRIAL` - Required to delete time trials

## Current Development Status

### ✅ Completed Features

1. **Database Schema:** Single DuckDB table with embedded proofs architecture
2. **Backend Commands:** Complete CRUD operations and embedded proof validation workflow
3. **API Endpoints:** Full REST endpoints including enhanced validation status computation
4. **Data Models:** Type-safe game-specific schemas with validation logic
5. **Frontend Submission:** Functional submission form with comprehensive proof handling
6. **Advanced Leaderboard System:** Complete implementation with:
   - Multi-filter system (track, country, validation status)
   - URL synchronization for shareable links
   - Player deduplication (best times only)
   - Platform-specific proof icons
   - Internationalized country names
   - Real-time client-side filtering
   - Responsive design
7. **Staff Validation Interface:** Working proof validation workflow
8. **Permission System:** Role-based access control integrated throughout
9. **Validation Status Logic:** Intelligent proof validation based on track + time verification

### 🚧 Current Limitations

1. **Multi-Game Support:** Currently focused primarily on Mario Kart World (architecture supports expansion)
2. **Player Analytics:** Individual player statistics pages not yet implemented

### ❌ Missing Features

1. **Player Statistics Dashboard:** Individual player analytics and performance tracking
2. **Advanced Analytics:** Historical trend analysis and comparative statistics  
3. **Enhanced Multi-Game Support:** Additional game-specific features beyond Mario Kart World
4. **Bulk Import/Export:** Mass data management capabilities

## Known Issues

The time trials implementation has been significantly improved, but some areas need attention:

### 1. **Legacy Code Cleanup**
- **Issue:** Some unused code paths and inconsistent patterns remain from earlier iterations
- **Impact:** Minimal - core functionality works correctly
- **Priority:** Low - cleanup rather than critical fixes

### 2. **Multi-Game Expansion**
- **Issue:** Feature is optimized for Mario Kart World
- **Details:** Architecture supports other games but requires additional configuration
- **Impact:** No functional issues for current use case

### 3. **Performance Optimization Opportunities**
- **Issue:** Client-side filtering could be moved to backend for very large datasets
- **Current State:** Works well for expected data volumes
- **Priority:** Future optimization rather than current problem

## Technical Debt

1. **Code Organization:** Some legacy code patterns that could be modernized
2. **Database Optimization:** Potential for query optimization as data grows
3. **Game Constants:** Track and game data could be moved to configuration files
4. **Caching Strategy:** Opportunity for performance improvements with larger datasets

## Future Development Priorities

Based on the current mature state, the following could enhance the feature further:

1. **Medium Priority: Player Statistics Dashboard** - Individual player analytics and performance tracking
2. **Medium Priority: Enhanced Multi-Game Support** - Expand features for other Mario Kart games
3. **Low Priority: Advanced Analytics** - Historical trends and comparative statistics
4. **Low Priority: Performance Optimization** - Backend filtering for very large datasets
5. **Low Priority: Bulk Operations** - Import/export capabilities for data management

## Integration Points

The time trials feature integrates with:

- **Player System:** Links to SQLite player records for identity via DuckDB ATTACH queries
- **Permission System:** Uses global permissions for access control  
- **Authentication:** Requires logged-in users with appropriate permissions
- **Internationalization:** Full i18n support including localized country names
- **URL Routing:** Deep linking support for shareable leaderboard configurations

## Feature Maturity Assessment

The Time Trials feature is now in a **production-ready state** with:

✅ **Core Functionality:** Complete submission, validation, and leaderboard systems  
✅ **User Experience:** Polished interface with advanced filtering and sharing  
✅ **Data Integrity:** Robust validation logic and proof verification  
✅ **Performance:** Efficient client-side filtering and responsive design  
✅ **Accessibility:** Internationalized interface with proper accessibility features  
✅ **Maintainability:** Clean architecture with room for future expansion  

This documentation reflects the current **mature implementation** of the time trials feature. The system provides a comprehensive solution for Mario Kart time trial management with room for future enhancements focused on player analytics and multi-game expansion.

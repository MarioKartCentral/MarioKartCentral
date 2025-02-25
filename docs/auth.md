# Authentication & Authorization

- [Core Concepts](#core-concepts)
  - [Scoped Permissions](#scoped-permissions)
  - [Role-Based Access](#role-based-access)
  - [Permission Resolution](#permission-resolution)
- [Implementation Details](#implementation-details)
  - [Database Schema](#database-schema)
  - [Permission Structure](#permission-structure)
  - [Role Management](#role-management)
  - [Usage Examples](#usage-examples)
  - [Adding New Permissions](#adding-new-permissions)
- [Security Considerations](#security-considerations)

This document describes how user authentication and authorization are implemented throughout MarioKartCentral. It covers the permission system, role management, and security considerations that protect access to resources across the application.

## Core Concepts

The auth system consists of three main components:

1. **Scoped Permissions**
   The system has four permission scopes:
   - Global: Affects all resources
   - Team: Controls team resource access
   - Series: Controls tournament series access  
   - Tournament: Controls tournament access
   
   Permission checks look at roles in each relevant scope. A tournament permission check includes tournament roles, series roles, and global roles.

2. **Role-Based Access**
   Each role contains:
   - A set of granted and denied permissions
   - A position number for management hierarchy
   - An optional scope (team, tournament, etc.)
   - The ability to override lower-scoped permissions

3. **Permission Resolution**
   For each permission check:
   - All roles in relevant scopes are combined
   - Both grants and denials are collected
   - Higher scopes override lower scopes
   - Access is denied by default

## Implementation Details

Roles and permissions are stored in scope-specific database tables (global, team, series, tournament). Each scope table follows the same structure, but permissions cascade down through the scopes - global permissions can override team permissions, but not vice versa. This hierarchy ensures that global admins maintain control while allowing granular permissions at each level.

The role system uses numeric positions to establish management chains - lower numbers can manage higher numbers. This means a role with position 1 can manage roles with positions 2+, but not vice versa. The system also supports temporary roles, primarily used for player bans, which are automatically removed by a background job.

### Database Schema

Each scope has a consistent set of tables:

```sql
-- Core role definition (same pattern for team_roles, series_roles, etc)
CREATE TABLE roles(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    position INTEGER NOT NULL  -- Lower numbers manage higher numbers
);

-- Role-Permission mapping with explicit grants/denials
CREATE TABLE role_permissions(
    role_id INTEGER NOT NULL REFERENCES roles(id),
    permission_id INTEGER NOT NULL REFERENCES permissions(id),
    is_denied BOOLEAN DEFAULT FALSE NOT NULL,
    PRIMARY KEY (role_id, permission_id)
) WITHOUT ROWID;

-- Global roles base table
CREATE TABLE user_roles(
    user_id INTEGER NOT NULL REFERENCES users(id),
    role_id INTEGER NOT NULL REFERENCES roles(id),
    expires_on INTEGER,  -- Unix timestamp
    PRIMARY KEY (user_id, role_id)
) WITHOUT ROWID;

-- Scoped role tables add scope_id
CREATE TABLE user_team_roles(
    user_id INTEGER NOT NULL REFERENCES users(id),
    role_id INTEGER NOT NULL REFERENCES team_roles(id),
    team_id INTEGER NOT NULL REFERENCES teams(id),
    expires_on INTEGER,
    PRIMARY KEY (user_id, role_id, team_id)
) WITHOUT ROWID;
```

### Permission Structure

The default stance is restrictive - all permissions must be explicitly granted unless using check_denied_only mode. This mode is used for self-service actions like editing your own profile or registering for tournaments, where access should be allowed by default unless explicitly denied.

Permission checks traverse the scope hierarchy in a specific order based on the resource type:
- For tournament resources: tournament → series → global
- For team resources: team → global
- For user resources: global only

This traversal follows strict rules:
- Global scope has ultimate authority
- Higher scopes can override denials from lower scopes
- Lower scopes cannot override higher scope denials
- A DENY in global scope is absolute and cannot be overridden

For a complete list of available permissions, see [`/src/backend/common/auth/permissions.py`](/src/backend/common/auth/permissions.py).

### Role Management

1. **Role Hierarchy**
   - Each role has a position number determining management hierarchy
   - Lower positions can manage higher positions
   - Users can't modify roles with positions lower than their own
   - Complete role definitions can be found in [`/src/backend/common/auth/roles.py`](/src/backend/common/auth/roles.py)

2. **Temporary Bans**
   - The expiration system is primarily used for implementing temporary player bans
   - Banned players are assigned a role that denies various permissions
   - A background job ([`/src/backend/worker/jobs/role_checker.py`](/src/backend/worker/jobs/role_checker.py)) automatically removes expired ban roles
   - Expiration is checked on a per-minute basis

### Usage Examples

Permission checks are implemented through decorators on backend endpoints:

```python
# Global permissions
@require_permission("manage_users")
@require_permission("edit_profile", check_denied_only=True)  # Permissive mode

# Scoped permissions
@require_team_permission("team_edit")
@require_series_permission("series_configure") 
@require_tournament_permission("tournament_seed")
```

The frontend implements permission checking using Svelte's if blocks:

```typescript
{#if check_permission(user_info, permissions.manage_user_roles)}
  <RoleManagement {user_info} {target_player} />
{/if}

{#if check_team_permission(user_info, permissions.manage_team_roles, team.id)}
  <TeamRoleManagement {user_info} {team} {roster} />
{/if}
```

The frontend checks are for UI purposes ONLY:
1. They only control what UI elements are shown/hidden
2. Every action must still validate permissions on the backend
3. Frontend checks can be bypassed and should never be relied upon for security

### Adding New Permissions

When adding a new feature that requires permission checks, follow these steps:

1. Define the permission constant in the appropriate file:
```python
# /src/backend/common/auth/permissions.py
MANAGE_FUN_FACTS = "fun_facts_manage"
```

2. Add it to relevant roles:
```python
# /src/backend/common/auth/roles.py
SITE_MODERATOR_PERMISSIONS = [
    permissions.MANAGE_FUN_FACTS,
]
```

3. Use it in an endpoint:
```python
@require_permission(permissions.MANAGE_FUN_FACTS)
async def delete_fun_fact(request: Request) -> JSONResponse:
    # Implementation
```

## Security Considerations

1. **Error Handling**
   - Authentication failures return an RFC 7807 Problem JSON response with status code 401 with "Invalid login details"
   - Authorization failures return status code 401 to prevent information leakage

2. **Password Security**
   - Passwords are hashed using Argon2id

3. **Session Management**
   - Session tokens are randomly generated
   - Sessions expire after 365 days
   - Sessions are stored in the database

4. **Performance**
   The current implementation performs fresh database queries for each permission check. Future optimizations could include:
   - Short-lived permission caching with careful invalidation
   - Denormalized permission views for common checks
   - Batch permission loading for UI operations
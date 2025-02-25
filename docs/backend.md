# Backend Architecture

- [Storage](#storage)
  - [SQLite Database](#sqlite-database)
  - [S3-Compatible Object Storage](#s3-compatible-object-storage)
- [Error Handling](#error-handling)
- [Common Library](#common-library)
  - [Command Pattern](#command-pattern)
- [Backend API](#backend-api)
  - [Model Binding and Validation](#model-binding-and-validation)
  - [Permission System](#permission-system)
  - [Request Handling Pattern](#request-handling-pattern)
  - [Background Tasks](#background-tasks)
  - [OpenAPI Schema Generation](#openapi-schema-generation)
- [Background Worker](#background-worker)
- [Complete Example: Fun Facts Feature](#complete-example-fun-facts-feature)

The backend consists of two Python services built on a shared library:

1. **Backend API**: A RESTful web service that handles all user interactions
2. **Background Worker**: A service that runs scheduled maintenance tasks

This document describes how these services work as well as how they interact with our storage systems.

## Storage

Data in the application is split between two storage systems based on access patterns and size requirements:

### SQLite Database
Primary storage for all structured data like:
- User accounts and permissions
- Game records and statistics
- Tournament structures and results
- Team rosters and memberships

For complete database structure details, see [Database Schema](database.md).

### S3-Compatible Object Storage 
Used for storing larger content where direct database access isn't required:
- Long text content (e.g., tournament rules, player biographies)
- Uploaded assets and files
- Historical data archives

Both storage systems are accessed exclusively through commands, keeping business logic separate from storage implementation details.

## Error Handling

The system uses a consistent error handling pattern that flows through all layers of the application:

1. Commands raise domain-specific errors with status codes:
```python
if len(self.fact) > CreateFunFactRequest.MAX_LENGTH:
    raise Problem(
        "Fun fact too long",
        f"Maximum length is {CreateFunFactRequest.MAX_LENGTH} characters",
        status=400
    )

if not row:
    raise Problem("User not found", status=404)
```

2. The API's middleware automatically converts these to RFC 7807 JSON responses:
```json
{
    "title": "Fun fact too long",
    "detail": "Maximum length is 500 characters",
    "status": 400
}
```

This ensures consistent error responses regardless of where in the stack the error originates, whether from commands, permission checks, or model validation.

## Common Library ([`/src/backend/common`](/src/backend/common/))

The common library acts as the core domain layer of our application, shared by both the API and worker services. This separation ensures that:

- Business logic is defined once and reused across services
- Data access patterns are consistent
- Domain models and validation are centralized
- Services remain focused on their specific concerns (HTTP or scheduling)

### Command Pattern ([`/common/data/commands`](/src/backend/common/data/commands/))

Commands are implemented using Python dataclasses and encapsulate a unit of work against the database. Each command has access to both database and S3 storage wrappers for persistence. Here's a simple example:

```python
@save_to_command_log
@dataclass
class GetPlayerNameCommand(Command[str | None]):
    player_id: int
    
    async def handle(self, db_wrapper, s3_wrapper) -> str | None:
        async with db_wrapper.connect() as db:
            async with db.execute(
                "SELECT name FROM players WHERE id = ?", 
                (self.player_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
```

Commands that modify data should be decorated with `@save_to_command_log` to enable:
- Audit trails for tracking changes
- Debugging of production issues 
- Data recovery capabilities

Note: Commands that handle sensitive data (like password hashes or auth tokens) should not use `@save_to_command_log` to prevent logging private information.

Commands are organized by domain (auth, players, teams, etc) and both the `api` and `worker` projects expose a `handle` function to execute commands with the necessary dependencies.

## Backend API ([`/src/backend/api`](/src/backend/api/))

The API service is built with Starlette and handles all user interactions with the system. It demonstrates several key architectural patterns:

### Model Binding and Validation

The API uses Python dataclasses from the `common/data/models` module to validate incoming requests. Two decorators handle automatic validation:

- `@bind_request_body`: Validates JSON request bodies
- `@bind_request_query`: Validates URL query parameters

For example, when listing fun facts, query parameters are automatically bound to a filter model:

```python
@dataclass 
class FunFactFilter:
    user_id: int | None = None
    page: int = 1
    page_size: int = 20

@bind_request_query(FunFactFilter)  
async def list_fun_facts(request: Request, filter: FunFactFilter) -> JSONResponse:
    command = ListFunFactsCommand(filter)
    facts = await handle(command)
    return JSONResponse(facts)
```

This endpoint can be called with `/api/fun-facts?user_id=123` and the parameters will be automatically validated and converted to the correct types.

### Permission System

The API uses a sophisticated permission system with several levels of access control decorators:

```python
# Basic permission check - user must have the permission granted
@require_permission(permissions.MANAGE_USER_ROLES)
async def list_roles(request: Request) -> JSONResponse:
    roles = await handle(ListRolesCommand())
    return JSONResponse(roles)

# Team-specific permission check
@require_team_permission(team_permissions.MANAGE_TEAM_ROLES)
async def remove_team_role_from_player(request: Request, body: RemoveRoleRequestData):
    # ...

# Tournament-specific permission check
@require_tournament_permission(tournament_permissions.MANAGE_TOURNAMENT_ROLES)
async def tournament_role_info(request: Request) -> JSONResponse:
    # ...

# Less restrictive permission check using check_denied_only
# When check_denied_only=True, the request is allowed as long as the user
# doesn't have an explicit DENY for the permission. This is useful for
# actions that should be allowed by default unless explicitly restricted.
@require_permission(permissions.EDIT_PROFILE, check_denied_only=True)
async def edit_settings(request: Request, body: EditUserSettingsRequestData):
    # ...
```

For more details on the permission system design, see [Authentication & Authorization](auth.md).

### Request Handling Pattern

API endpoints in our architecture follow a strict separation of concerns pattern that enhances maintainability and testability. Looking at our Fun Facts feature as an example:

1. **HTTP Layer (Endpoints)**
   - Routes define URL structure (`/api/fun-facts`)
   - `@bind_request_body` validates the CreateFunFactRequest model
   - `@check_word_filter` moderates content
   - `@require_permission` checks user access
   - Response formatting and status codes

2. **Business Logic (Commands)**
   - CreateFunFactCommand handles database operations
   - Validates fact length and user existence
   - Returns domain objects (FunFact and username)
   - Can be reused by other endpoints or worker jobs

See the Background Tasks section for how we handle operations that should occur after the response is sent.

This separation allows us to:
- Test business logic independently of HTTP concerns
- Reuse commands across different contexts
- Change HTTP interfaces without touching business logic
- Keep endpoint code focused and consistent

### Background Tasks

The API supports running background tasks that execute after the response has been sent to the client. This pattern complements our Background Worker service by handling one-off tasks that are specific to a request, while the worker handles scheduled, repeating tasks. Both use the same command pattern for consistency.

Tasks are useful for operations that:
- Aren't critical to the main request
- May take longer to complete
- Shouldn't affect the response time

Tasks are defined as async functions and attached to responses:
```python
async def example_endpoint(request: Request) -> JSONResponse:
    async def cleanup():
        # Background task won't affect response time
        await handle(CleanupTempFilesCommand())

    # Main request logic
    result = await handle(MainOperationCommand())
    
    # Attach background task to response
    return JSONResponse(
        result, 
        status_code=200,
        background=BackgroundTask(cleanup)
    )
```

Common uses for background tasks include:
- Sending notifications
- Cleaning up temporary resources
- Updating cached values
- Logging activity

For a complete example of background tasks in action, see the Fun Facts feature at the end of this document.

### OpenAPI Schema Generation

The API automatically generates an OpenAPI schema by inspecting:
- Route definitions and path parameters
- Request body models from `@bind_request_body`
- Query parameter models from `@bind_request_query`

This schema is available at `/api/schema` and powers the Swagger UI for testing at `/swagger/`.

## Background Worker ([`/src/backend/worker`](/src/backend/worker/))

The worker service provides a simple job scheduling system for running periodic tasks. Jobs implement a base `Job` class with properties for name and delay interval, plus an async run method that contains the job's logic. The worker runs jobs on a continuous loop, checking each job's delay to determine when to run it next. Jobs that take longer than their delay interval to complete are logged as warnings.

Here's an example of defining a job:

```python
class RemoveExpiredRolesJob(Job):
    @property
    def name(self) -> str:
        return "Remove Expired Roles"
    
    @property
    def delay(self) -> timedelta:
        return timedelta(minutes=1)  # Check every minute
    
    async def run(self):
        # Jobs use the same command pattern as the API
        await handle(RemoveExpiredRolesCommand())
```

Like the API endpoints, worker jobs use the same command pattern and access the same storage systems. This shared architecture means business logic can be reused across both synchronous API requests and background processing. For example, in the Fun Facts feature at the end of this document, both the API endpoint and its background notification task use the same command pattern to interact with the database.

## Complete Example: Fun Facts Feature

Let's walk through implementing a complete feature that ties together the architectural patterns we've covered. We'll create a system that lets users share random fun facts about themselves and notify their followers when they do.

1. Define the Models
```python
# common/data/models/fun_facts.py
from dataclasses import dataclass

@dataclass
class FunFact:
    id: int
    user_id: int
    fact: str
    created_at: int
    
@dataclass
class CreateFunFactRequest:
    fact: str
    # Facts will be stored in database, so keep size reasonable
    MAX_LENGTH = 500

@dataclass 
class FunFactFilter:
    user_id: int | None = None
    page: int = 1
    page_size: int = 20
```

2. Create the Database Table
```python
# common/data/db/tables/fun_facts.py
from dataclasses import dataclass
from common.data.db import TableModel

@dataclass
class FunFactTable(TableModel):
    @staticmethod
    def get_create_table_command() -> str:
        return """CREATE TABLE IF NOT EXISTS fun_facts(
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            fact TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )"""
```

3. Implement the Commands
```python
# common/data/commands/fun_facts.py
from dataclasses import dataclass
from datetime import datetime, timezone
from common.data.commands import Command, save_to_command_log
from common.data.models import Problem, FunFact, CreateFunFactRequest

@save_to_command_log
@dataclass
class CreateFunFactCommand(Command[tuple[FunFact, str]]):
    user_id: int
    fact: str
    
    async def handle(self, db_wrapper, s3_wrapper):
        if len(self.fact) > CreateFunFactRequest.MAX_LENGTH:
            raise Problem(
                "Fun fact too long",
                f"Maximum length is {CreateFunFactRequest.MAX_LENGTH} characters",
                status=400
            )
            
        created_at = int(datetime.now(timezone.utc).timestamp())
        
        async with db_wrapper.connect() as db:
            # Check if user exists
            async with db.execute("SELECT name FROM users WHERE id = ?", (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("User not found", status=404)
                user_name = row[0]
            
            # Insert the fun fact
            result = await db.execute_insert(
                "INSERT INTO fun_facts(user_id, fact, created_at) VALUES (?, ?, ?)",
                (self.user_id, self.fact, created_at)
            )
            if not result:
                raise Problem("Failed to create fun fact")
                
            fact_id = result[0]
            await db.commit()
            
            return (
                FunFact(fact_id, self.user_id, self.fact, created_at),
                user_name
            )

@dataclass
class ListFunFactsCommand(Command[list[FunFact]]):
    filter: FunFactFilter
    
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            offset = (self.filter.page - 1) * self.filter.page_size
            query = """
                SELECT id, user_id, fact, created_at 
                FROM fun_facts 
                WHERE COALESCE(user_id = ?, TRUE)
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            
            facts = []
            params = [self.filter.user_id, self.filter.page_size, offset]
            async with db.execute(query, params) as cursor:
                async for row in cursor:
                    facts.append(FunFact(*row))
                    
            return facts
```

4. Create the API Endpoint
```python
# api/endpoints/fun_facts.py
from starlette.requests import Request
from starlette.routing import Route
from starlette.background import BackgroundTask
from api.auth import require_logged_in, require_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from api.utils.word_filter import check_word_filter
from common.data.commands import *
from common.data.models import *
from common.auth import permissions
import common.data.notifications as notifications

@bind_request_body(CreateFunFactRequest)
@check_word_filter  # Check for inappropriate content
@require_permission(permissions.EDIT_PROFILE, check_denied_only=True)
async def create_fun_fact(request: Request, body: CreateFunFactRequest) -> JSONResponse:
    async def notify():
        # Notify followers that a new fun fact was posted
        followers_command = GetUserFollowersCommand(user_id)
        followers = await handle(followers_command)
        if followers:
            content_args = {'user': user_name, 'fact': body.fact}
            notify_command = DispatchNotificationCommand(
                followers,
                notifications.NEW_FUN_FACT,
                content_args,
                f'/profile?id={user_id}',
                notifications.INFO
            )
            await handle(notify_command)

    user_id = request.state.user.id
    create_command = CreateFunFactCommand(user_id, body.fact)
    fun_fact, user_name = await handle(create_command)
    return JSONResponse(fun_fact, status_code=201, background=BackgroundTask(notify))

@bind_request_query(FunFactFilter)
async def list_fun_facts(request: Request, filter: FunFactFilter) -> JSONResponse:
    list_command = ListFunFactsCommand(filter)
    facts = await handle(list_command)
    return JSONResponse(facts)

routes = [
    Route('/api/fun-facts', create_fun_fact, methods=['POST']),
    Route('/api/fun-facts', list_fun_facts)
]
```

This example demonstrated key architectural principles:
- Commands encapsulate all business logic and data access
- Models provide consistent validation
- Endpoints remain thin and focused on HTTP concerns
- Permissions protect data appropriately
- Background tasks handle non-critical operations
- Error handling flows consistently through all layers

These patterns help keep our codebase maintainable and testable as it grows.
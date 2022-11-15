# System Design
## Preface
When working in traditional companies and organisations, it tends to be quite easy to justify spending hundreds or thousands of dollars per month on hosting a website. The reason it costs so much is because services like Azure, AWS, and Google Cloud Platform offer a large suite of services to solve all kinds of common problems that people solve. In addition, they offer great support and it saves lots of developer time as they don't need to be mucking around with all kinds of server maintenance tasks.

Unfortunately, when it comes to making a website for a community that does not have that kind of money to spend on web hosting, we do not have the luxury of using these off-the-shelf systems and so you need to manage this all by yourself. This is the reality we are going to have to face with this project, and at any given moment the monetary cost of a solution is likely to be the largest factor in making architectural decisions.

If you were building a site for less than 100 users or so, this is quite easy to achieve. All you need to do is build an app that serves a front-end and a back-end, has a local database sitting next to it on the file system, and either self-host on someone's computer or deploy it to a cheap cloud VM provider and expose the port. But we don't have this luxury either as we need to build a site that can support 10,000 to 100,000 people. It also needs to handle a constant stream of API requests from our discord bots, and very bursty traffic that can occur around the events that we run.

### Principles

With this in mind, here are a few principles to follow when designing new features:
- Offload as much computation as possible onto the client-side
  - This will mostly come in the form of page rendering
  - This could also come in the form of applying complicated filters over lots of data
- Serve and cache as much data as possible through the CDN
  - If a request is able to be fully handled by the CDN and it's cache, then that means less CPU usage on the server
  - The more requests handled by the CDN, the cheaper
- Centralise the data
  - If you keep all of your data in one place, then you can avoid all the pain that comes with distributed systems.
  - In our case, all relational data is stored in a single SQLite db, all other data is stored in an object storage with redis instance acting as an index over the object storage.
- Prerender as much of the site as possible
  - While this is primarily for client-side performance, if we can put as much data as possible inside the HTML that gets served to the user it means less API calls the user has to make, and a faster website
- Pre-cache expensive queries
  - An example of an expensive query would be ranking all the players in lounge to generate a leaderboard.
  - Make use of scheduled, background tasks to pre-cache these expensive queries and then use the cache in the API
- Only put data that needs atomicity, or will be queried on every request in the SQLite db
  - Relational databases get very slow and use lots of CPU the more data and the more queries they need to handle
  - An example of data where atomicity is important is user IDs, we want to ensure that two people who sign up at the same time can't be given the same user ID
  - An example of data that is queried on every request is permissions data, we need to check on every request if the user is authorised to perform the action
  - An example of data that does not fit into this is lounge match results or time trial information.
- All other data should go in our object storage
  - We are using [Wasabi](https://wasabi.com/cloud-storage-pricing/#three-info) for this because of their competitive pricing and no egress fees
- Redis should be used to allow for querying over data in the object storage
  - For example, full time trial data will go in the object storage, but redis can act as an index over the data so that we can perform queries over time trial information
- Asynchronicity everywhere
  - We should ensure that every time we make a call that could block the CPU (File I/O, Network, SQLite), it should be done asynchronously
  - In Python, this means using the async-await keywords.
  - I highly recommend watching [this talk](https://www.youtube.com/watch?v=F19R_M4Nay4) to understand how Python's async/await works
- Make data in the object storage immutable if possible
  - If data can be mutable, then we never know if we have the latest version and will need to request it again periodically
  - Browsers and CDNs can be told if data is immutable and handle caching appropriately
  - If data needs to be changed, then put it under a new file name and ensure that the API or the front-end points to the new file
  - If the data changes frequently, then it is ok for it to be mutable
    - If only one field is changing in a file with many fields, then see if we can move that field out of the file so that the rest of it can be stored immutably.

## User Accounts

All users will be given a unique integer ID upon account creation. User IDs will be allocated incrementally as new users create accounts on the site. Users will register and log in only using an email address and a password. The user ID should be used as a permanent, unchange-able identifier for an account, as people may change their email address at a later date. Passwords are stored inside the database using argon2 hashes.

Users should not be confused with "players", not all users of the site are players (they may be a user that represents a discord bot), and not all players are users (we may have data about a player despite them not having an account on our site). A user will be associated with up to one player, and a player will be associated with up to one user. Usernames will be associated with the "player" rather than the "user".

The following two tables exist in the SQLite database to encode this relationship

```sql
CREATE TABLE IF NOT EXISTS players(
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL)

CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    email TEXT UNIQUE,
    password_hash TEXT)
```

Note that more columns may get added to these tables if we believe that there is a need for them for performance or to support atomic operations while maintaining referential integrity.

When deciding whether new fields should be tied to the "player" or tied to the "user", it would be easy to answer by considering whether or not it makes sense for the data to be provided for users that aren't players or players that aren't users. For example, nationality makes sense being tied to a player, whereas language makes sense being tied to user as it changes what language they see the website when logged in.

## Authentication

Authentication is the process by which we verify who is making a request. For our site, we are just using session cookies. The way session cookies work is that when you log on to the site we will generate a random number and send it back using a "Set-Cookie" header so that it gets stored in your cookies. The backend keeps track of all the current sessions for all the users, so that when you open a new page we look at the cookie value being sent in the request, then look it up in the database to see what user corresponds to that session id.

Currently this is being stored inside a table in the SQLite, however if this table starts growing large we may consider moving it to redis instead.

```sql
CREATE TABLE IF NOT EXISTS sessions(
    session_id TEXT PRIMARY KEY NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    expires_on INTEGER NOT NULL) WITHOUT ROWID
```

## Authorization
Authorization is the proces by which we verify that the current user is allowed to perform the given action. The approach we are using is role based access control (RBAC). Users will be granted roles which will then give them additional permissions. Roles are assigned a set of permissions, and so when an API request is performed, we need to check if the user has a role which has the required permission. 

This is encoded using the following tables in the SQLite database:

```sql
CREATE TABLE IF NOT EXISTS roles(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL)

CREATE TABLE IF NOT EXISTS permissions(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL)

CREATE TABLE IF NOT EXISTS user_roles(
    user_id INTEGER NOT NULL REFERENCES users(id),
    role_id INTEGER NOT NULL REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)) WITHOUT ROWID

CREATE TABLE IF NOT EXISTS role_permissions(
    role_id INTEGER NOT NULL REFERENCES roles(id),
    permission_id INTEGER NOT NULL REFERENCES permissions(id),
    PRIMARY KEY (role_id, permission_id)) WITHOUT ROWID
```

An example of a permission might be `"grant_administrator"`, and so when an API call is made to grant someone the role of administrator, we check if the user has any roles which have this permission.

We can combine authentication and authorization into a single SQL query as follows where we see if a user with a given session id has the given permission:

```python
db.execute("""
    SELECT EXISTS(
        SELECT 1 FROM roles r
        JOIN user_roles ur ON ur.role_id = r.id
        JOIN users u on ur.user_id = u.id
        JOIN sessions s on s.user_id = u.id
        JOIN role_permissions rp on rp.role_id = r.id
        JOIN permissions p on rp.permission_id = p.id
        WHERE s.session_id = ? AND p.name = ?
    )""", (session_id, permission_name))
```

In the future, we will have roles that apply only to specific resources. For example, teams will have leaders/managers, events will have their organizers, or we may have roles tied to specific games. To handle these, we need to add new tables to store roles and permissions for each type of resource.

## Player Data and Registry
Player entities will have all sorts of extra information associated with them including username, friend code, country, and profile picture. Some of these fields will be stored in the SQLite database while others may be stored in the object storage.

The data can be served to users in three formats:
- Minimal
  - Used for scenarios such as tables, time trial leaderboards, lounge leaderboards
  - Consists only of player ID, name, and country
  - Used for majority of API requests
  - Should be served directly from SQLite DB
- Basic
  - Used for scenarios such as the player registry listing or team/squad roster
  - Includes additional data such as friend code, ban status
  - Next most common format
  - Data should be stored in object storage, but cached in redis for efficient querying
- Detailed
  - Used for the player's registry page
  - Contains every bit of player information we have, including bio, profile picture, tournament history, etc.
  - Least common format
  - Only supports looking up an exact player ID
  - Data stored and served from object storage without redis
  - Endpoints that return this data have should long cache expiration times so we can take advantage of browser and CDN caches.

The player registry is a page which allows people to filter, sort, and paginate through all the players on the site. As mentioned, we are going to be storing all the data needed for the registry page in the object storage, but cached in redis. At this early stage, this should be fine and we should not need any more caching on top of this. If we notice that this API call starts to cause us performance issues, we can look into pre-building some popular queries then making the clientside filter on those query results.

## Tournaments
Tournaments are a core component of the site, and includes in it lots of features that need to be supported. Below are links to the data design and API design for the tournaments functionality:

- [Data Design](https://github.com/MarioKartCentral/MarioKartCentral/issues/47)
- [API Design](https://github.com/MarioKartCentral/MarioKartCentral/issues/62)

Much like the player data, tournament data can be served in different formats:
- Minimal
  - Used for scenarios such as event calendars or for a player's tournament history
  - Consists of tournament id, name, date, game, and status (completed/active?) are all that is needed
    - For tournament history, there may be some additional data containing information about the team or outcome of the player in the tournament
  - Should be served directly from the SQLite db
- Basic
  - Used for the tournament registry
  - Contains extra information such as a short description of the tournament, the series it belongs to, and the logo
  - Cached in redis, but may be stored in either object storage or SQLite db depending on if the tournament is active
- Detailed
  - Used for the tournament details page
  - Contains all information about the tournament including sign-up information
  - Stored either in object storage or SQLite db depending on if the tournament is active

One thing that's nice about tournaments is that once a tournament has completed, it is very rare for people to make API requests for them unless it's a user going through some old results. When it comes to designing how the data is stored and queried, we should go with different approaches depending on if the tournament is active or if it has completed.

When a tournament has completed, it is likely that all the data related to it is immutable and won't change any more, so we can safely store all the data including sign-ups and team rosters inside our object storage and mark it as immutable to take advantage of browser and CDN caching.

For tournaments that are active and still taking sign-ups, some parts of the data may be changing frequently and so we can't store it immutably as the object storage is not a good place to store data that changes often. Some parts of the data may not change frequently though such as the tournament description and could be stored in the object storage. This is unlikely to be needed though since the number of active tournament at any given time is likely going to be small and there is little risk we will have performance issues storing all this data in the SQLite db.

### Teams and Squads
Tournaments will allow sign-ups from either individuals, squads or teams. Squads and teams are almost identical except that teams are not tied to a specific tournament, whereas squads are only applicable to the tournament they sign up for. In addition, squads may restrict the number of players to an exact amount (e.g. a 2v2 FFA will only allow squads containing two people).

Team data should be stored entirely in the SQLite database, this includes team rosters and team roles. Over time we can see if this is causing any performance issues and look into moving parts of the team data into object storage.

Squad data should also be stored in the SQLite database, but only for events that are still allowing sign-ups. Once sign-ups have closed for a tournament, all the squad data should be stored in object storage and deleted from the SQLite database.

For tournaments that allow sign-ups from teams, a snapshot of the team at the registration close data should be taken and stored in the object storage. This snapshot can then be treated as a squad that is linked to a team. By treating this snapshot as a squad, it should help make coding simpler rather than having to do checks to see if a tournament is a squad or team tournament all over the codebase.

It is still a topic of discussion, but there is debate over whether a player is allowed to be in multiple teams. For example, a player may have a team that they play with for MKU, while they have another team that they play with in Japanese tournaments. As long as both teams that the player is in don't play in the same tournament, then there is no strong reason a player shouldn't be allowed in multiple teams. However, if a scenario arises where a player is in two teams for the same tournament, they may be forced to leave one of the teams.

There will also exist a team registry page that will have a simliar look and feel to the player registry page. For the team registry page, since all the data is stored inside the SQLite db, it may be fine for API calls to directly access the SQLite db rather than having to use the redis cache. We should evaluate this over time in case performance issues arise.

## Time Trials and Records
Time trials form the other core component of the site. Not only do we need to store the records, but we will have lots and lots of leaderboards such as:

- Leaderboards per track
  - Multiple categories (e.g. NITA, glitch)
- Player rankings per game
  - Multiple ranking strategies (e.g. Average Finish, Sum of Times)

It is likely we will end up with millions of time trials on the site over time, and so it is not efficient to generate all these leaderboards on the fly every time someone opens a page on the site. Time trials also have lots of data attached to them, as outlined in [the Time Trials Data Design issue](https://github.com/MarioKartCentral/MarioKartCentral/issues/48).

Unlike the player/team/tournament registry pages which only support filters on a few properties, time trial leaderboards may support filters on almost any property of the TT including: game, track, mode, category, proof types, combination used, submission date, controller type etc. Combining this with having potentially millions of time trials in total, it will not be practical for us to store all of this data in SQLite or redis.

The solution we will go with is by pre-generating a set of default leaderboards as static JSON files which are stored in the object storage. Whenever a user needs to fetch a leaderboard, it sends a query to the API which will send back a path to a static JSON file for one of the default leaderboards. The client-side should fetch this file to get all the time trials then apply all the filters again on what it downloaded to make the leaderboard that gets displayed to the user.

As an example, say that a user wants to get a leaderboard of all the shroomless Waluigi Wiggler times on a specific track, they will fetch a static JSON file containing all the time trials for the track, then it will filter that JSON down on the client-side to only show shroomless times using Waluigi Wiggler.

These default leaderboards should be generated by a separate process to the API so that it doesn't steal CPU time that can be used to handle requests. Whenever a new time trial has been approved by one of the verifiers, that time trial will sit inside a table in SQLite which represents a queue of all the unprocessed time trials. On a schedule (say, every 10 minutes), the separate process will query this table to get all the unprocessed time trials, it will then update all the default leaderboards that are relevant to that time trial, then it will remove the time from the queue.

This approach may sound like it would cause all the leaderboards to potentially be out-of-date by up to 10 minutes depending on how recently the background schedule has been run. The solution to this is to make it so that the API call that gives us the URL of the JSON to fetch, can also send back all the entries from the unprocessed time trials queue, then the clientside will be able to merge them into the leaderboard.

This all might sound a bit overkill, but a similar approach of pre-caching all the leaderboards is used by MKLeaderboards today for this same reason, this is not something that we should do in the future as an optimisation, as it is my belief that we will start struggling with leaderboard generation performance immediately if we don't go with the approach outlined here.
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

## Registry Architecture
TODO

## Tournaments Architecture
TODO

## Time Trials Architecture
TODO

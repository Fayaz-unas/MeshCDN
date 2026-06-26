# TRACKER ARCHITECTURE HANDBOOK

**MeshCDN Tracker Server - Complete Technical Reference**

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Overview](#2-repository-overview)
3. [Architecture Overview](#3-architecture-overview)
4. [Database Schema](#4-database-schema)
5. [Folder Documentation](#5-folder-documentation)
6. [File-by-File Documentation](#6-file-by-file-documentation)
7. [API Endpoints](#7-api-endpoints)
8. [Data Models](#8-data-models)
9. [Service Layer](#9-service-layer)
10. [Repository Layer](#10-repository-layer)
11. [Background Tasks](#11-background-tasks)
12. [Configuration & Startup](#12-configuration--startup)
13. [Data Flow](#13-data-flow)
14. [Sequence Diagrams](#14-sequence-diagrams)
15. [Design Decisions](#15-design-decisions)
16. [Error Handling](#16-error-handling)
17. [Performance Considerations](#17-performance-considerations)
18. [Security Analysis](#18-security-analysis)
19. [Future Roadmap](#19-future-roadmap)
20. [Developer Guide](#20-developer-guide)

---

## 1 Project Overview

### Purpose

The MeshCDN Tracker is a **centralized coordination service** that maintains the global registry of peers in the network. It does NOT participate in file transfer; instead, it:
- Maintains a list of registered peers
- Tracks peer online/offline status via heartbeats
- Returns peer lists to peers requesting network information
- Handles peer identity management and conflict resolution

### Vision

The Tracker serves as the **discovery backbone** of the MeshCDN network. In a production system, multiple tracker instances may be deployed for redundancy, but the current implementation is a single-instance HTTP server.

### Goals

1. **Peer Registration**: Accept and store peer registrations with metadata (host, port, identity)
2. **Status Tracking**: Maintain peer online/offline status based on heartbeat presence
3. **Peer Discovery**: Serve lists of peers to peers requesting network information
4. **Identity Conflict Resolution**: Prevent duplicate registration of same peer/installation
5. **High Availability**: Accept many concurrent requests for peer list
6. **Scalability**: Support thousands of peers efficiently

### Non-Goals

1. **File Indexing**: Tracker does not know what files exist; peers share files directly
2. **Content Caching**: No caching of files; only metadata tracking
3. **BitTorrent Compatibility**: Not a BitTorrent tracker (uses HTTP instead of binary protocol)
4. **Distributed/DHT**: Single centralized instance (DHT is future goal)

### Core Concepts

#### Peer Registration
When a peer starts, it calls the `/register-peer` endpoint with its `peer_id`, `installation_id`, and `port`. The Tracker stores this metadata along with the IP address extracted from the request.

#### Heartbeat
Every N seconds (default 30), peers call the `/heartbeat` endpoint to signal they're still online. The Tracker updates the peer's `last_seen` timestamp.

#### Peer Cleanup Task
A background task runs every 30 seconds and marks peers as "offline" if their `last_seen` is older than 60 seconds. Offline peers are still queryable but marked with `status="offline"`.

#### Peer Discovery
When a peer needs to find other peers, it calls the `/peers` endpoint. The Tracker returns a list of all registered peers (both online and offline). The calling peer filters as needed.

---

## 2 Repository Overview

### Complete Repository Tree

```
backend/tracker/
│
├── app/
│   ├── main.py                          [FASTAPI APP INITIALIZATION]
│   │
│   ├── core/
│   │   ├── config.py                    [CONFIGURATION (EMPTY)]
│   │   └── __init__.py
│   │
│   ├── db/
│   │   ├── base.py                      [SQLALCHEMY DECLARATIVE BASE]
│   │   ├── database.py                  [DATABASE ENGINE & SESSION]
│   │   ├── dependencies.py              [DEPENDENCY INJECTION]
│   │   └── __pycache__/
│   │
│   ├── models/
│   │   ├── peer.py                      [PEER DATABASE MODEL]
│   │   ├── __init__.py
│   │   └── __pycache__/
│   │
│   ├── schemas/
│   │   ├── peer_schema.py               [PYDANTIC REQUEST SCHEMAS]
│   │   ├── heartbeat_schema.py          [HEARTBEAT REQUEST SCHEMA]
│   │   └── __pycache__/
│   │
│   ├── repositories/
│   │   ├── peer_repository.py           [DATA ACCESS LAYER]
│   │   └── __pycache__/
│   │
│   ├── services/
│   │   ├── peer_service.py              [BUSINESS LOGIC LAYER]
│   │   └── __pycache__/
│   │
│   ├── api/
│   │   ├── peer_routes.py               [HTTP ENDPOINTS]
│   │   └── __pycache__/
│   │
│   ├── tasks/
│   │   ├── peer_cleanup.py              [BACKGROUND CLEANUP TASK]
│   │   └── __pycache__/
│   │
│   ├── test.py                          [TEST FILE]
│   └── __pycache__/
│
├── .env                                  [ENVIRONMENT VARIABLES]
├── .venv/                                [PYTHON VIRTUAL ENV]
├── requirements.txt                      [PYTHON DEPENDENCIES]
└── __pycache__/
```

### Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.136.3 | Web framework and routing |
| `uvicorn` | 0.49.0 | ASGI server |
| `sqlalchemy` | (via ORM) | Database ORM |
| `pydantic` | 2.13.4 | Request/response validation |
| `starlette` | 1.2.1 | Web toolkit (used by FastAPI) |

### Architecture Layers

```
┌──────────────────────────────────────┐
│      HTTP CLIENTS (Peers)            │
├──────────────────────────────────────┤
│       FASTAPI APPLICATION            │
│  app/main.py - Router setup          │
├──────────────────────────────────────┤
│       API LAYER (api/)               │
│  peer_routes.py - Endpoints          │
├──────────────────────────────────────┤
│      SERVICE LAYER (services/)       │
│  peer_service.py - Business logic    │
├──────────────────────────────────────┤
│    REPOSITORY LAYER (repositories/)  │
│  peer_repository.py - Data access    │
├──────────────────────────────────────┤
│    SCHEMA LAYER (schemas/)           │
│  Pydantic models for validation      │
├──────────────────────────────────────┤
│      DATABASE LAYER (db/)            │
│  SQLAlchemy models & engine          │
├──────────────────────────────────────┤
│   BACKGROUND TASKS (tasks/)          │
│  Cleanup operations on timer         │
├──────────────────────────────────────┤
│      EXTERNAL SYSTEMS                │
│  - Database (SQLite/PostgreSQL)      │
│  - Network (HTTP)                    │
└──────────────────────────────────────┘
```

---

## 3 Architecture Overview

### System Architecture Diagram

```
                     ┌─────────────────────────────┐
                     │    TRACKER SERVICE          │
                     │  (HTTP Server - FastAPI)    │
                     └──────────┬──────────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                  /peers    /register   /heartbeat
                  (GET)     (POST)      (POST)
                    │           │           │
        ┌───────────┴───────────┴───────────┴──────────┐
        │                                               │
        │   ┌──────────────────────────────┐           │
        │   │   FASTAPI ROUTERS            │           │
        │   │   app/api/peer_routes.py     │           │
        │   └──────────────┬───────────────┘           │
        │                  │                           │
        │   ┌──────────────▼───────────────┐           │
        │   │   SERVICE LAYER              │           │
        │   │   PeerService                │           │
        │   │  - register_peer()           │           │
        │   │  - get_all_peers()           │           │
        │   │  - heartbeat()               │           │
        │   │  - mark_inactive_peers()     │           │
        │   └──────────────┬───────────────┘           │
        │                  │                           │
        │   ┌──────────────▼───────────────┐           │
        │   │   REPOSITORY LAYER           │           │
        │   │   PeerRepository             │           │
        │   │  - get_by_peer_id()          │           │
        │   │  - create_peer()             │           │
        │   │  - update_peer()             │           │
        │   │  - get_all_peers()           │           │
        │   └──────────────┬───────────────┘           │
        │                  │                           │
        │   ┌──────────────▼───────────────┐           │
        │   │   DATABASE MODELS            │           │
        │   │   models/peer.py             │           │
        │   │   - Peer ORM model           │           │
        │   └──────────────┬───────────────┘           │
        │                  │                           │
        │                  ▼                           │
        │   ┌──────────────────────────┐              │
        │   │   SQLAlchemy Engine      │              │
        │   │   SQLite / PostgreSQL    │              │
        │   │                          │              │
        │   │   TABLE: peers           │              │
        │   │   - id (PK)              │              │
        │   │   - peer_id (UQ)         │              │
        │   │   - installation_id (UQ) │              │
        │   │   - ip_address           │              │
        │   │   - port                 │              │
        │   │   - status               │              │
        │   │   - created_at           │              │
        │   │   - last_seen            │              │
        │   └──────────────────────────┘              │
        │                                              │
        └──────────────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
    BACKGROUND TASK            Response to Peers
    Cleanup (every 30s)        (peer list)
```

---

## 4 Database Schema

### Peer Table (Complete)

```sql
CREATE TABLE peers (
    id BIGINT PRIMARY KEY AUTOINCREMENT,
    peer_id VARCHAR(100) UNIQUE NOT NULL,
    installation_id VARCHAR(100) UNIQUE NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    port INTEGER NOT NULL,
    status VARCHAR(10) NOT NULL DEFAULT 'online',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Column Descriptions

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | BIGINT | PK, AUTO_INCREMENT | Internal database identifier |
| `peer_id` | VARCHAR(100) | UNIQUE, NOT NULL | Unique peer identifier (e.g., "peer_abc123") |
| `installation_id` | VARCHAR(100) | UNIQUE, NOT NULL | Instance identifier; prevents duplicate installations |
| `ip_address` | VARCHAR(45) | NOT NULL | IPv4 or IPv6 address of peer |
| `port` | INTEGER | NOT NULL | TCP port where peer server listens |
| `status` | VARCHAR(10) | NOT NULL, DEFAULT "online" | "online" or "offline" |
| `created_at` | DATETIME | NOT NULL, DEFAULT NOW | Registration timestamp |
| `last_seen` | DATETIME | NOT NULL, DEFAULT NOW | Last heartbeat timestamp |

### Key Constraints and Indices

- **Primary Key**: `id` (auto)
- **Unique Constraints**: `peer_id` and `installation_id` (prevent duplicates)
- **Default Values**: `status = "online"`, timestamps default to current time
- **Recommended Indices**: `(peer_id)`, `(status, last_seen)` for cleanup queries

### Invariants

1. **Peer ID Uniqueness**: Only one active record per `peer_id` at any time
2. **Installation ID Uniqueness**: Only one active record per `installation_id` at any time
3. **Status Values**: Must be "online" or "offline" (enforced in service layer, not DB)
4. **IP/Port Validity**: Assumed valid (no validation in DB; validated in service)

---

## 5 Folder Documentation

### `core/`

**Purpose**: Configuration and setup files

**Files**:
- `config.py`: Empty (future location for environment-based config)
- `__init__.py`: Package marker

**Rationale**: Separates configuration concerns from application logic. Currently unused; in future can hold Pydantic Settings models for environment-based config.

### `db/`

**Purpose**: Database initialization and connection management

**Files**:
- `base.py`: SQLAlchemy DeclarativeBase for ORM models
- `database.py`: Engine creation and SessionLocal factory
- `dependencies.py`: get_db() dependency injection for FastAPI
- `__pycache__/`: Python bytecode cache

**Key responsibilities**:
- Create database engine from `DATABASE_URL` environment variable
- Provide database sessions to routes via dependency injection
- Define declarative base for all models to inherit from

**Design rationale**: 
- Centralizes database configuration in one place
- FastAPI dependency injection pattern (`get_db()`) ensures proper session cleanup
- `pool_pre_ping=True` validates connections before use (reconnects if stale)

### `models/`

**Purpose**: SQLAlchemy ORM models representing database tables

**Files**:
- `peer.py`: Peer ORM model
- `__init__.py`: Package marker

**Rationale**: ORM models are separate from request schemas (schemas are in `schemas/`)

### `schemas/`

**Purpose**: Pydantic models for request/response validation

**Files**:
- `peer_schema.py`: `PeerRegistrationRequest` validation
- `heartbeat_schema.py`: `HeartbeatRequest` validation

**Rationale**: Separate from ORM models to allow flexibility in API contracts independent of database schema

### `repositories/`

**Purpose**: Data access layer

**Files**:
- `peer_repository.py`: All database queries for peers

**Rationale**: Isolates database queries in one place; makes testing easier and changes to queries localized

### `services/`

**Purpose**: Business logic layer

**Files**:
- `peer_service.py`: `PeerService` with registration, heartbeat, cleanup logic

**Rationale**: Services orchestrate repository calls and implement idempotency, conflict detection, and status updates

### `api/`

**Purpose**: HTTP endpoint definitions

**Files**:
- `peer_routes.py`: `/register-peer`, `/peers`, `/heartbeat` endpoints

**Rationale**: Fastapi routers separate endpoint definitions from business logic

### `tasks/`

**Purpose**: Background asynchronous tasks

**Files**:
- `peer_cleanup.py`: Periodic cleanup task marking inactive peers as offline

**Rationale**: Runs in parallel with web server via asyncio; not blocking request handling

---

## 6 File-by-File Documentation

### app/main.py

**Purpose**: FastAPI application initialization and startup/shutdown lifecycle

**Complete Code Explanation**:

```python
from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI

from app.api.peer_routes import router as peer_router
from app.tasks.peer_cleanup import cleanup_inactive_peers
```

Lines 1-6: Imports
- `asynccontextmanager`: Decorator for async context managers (setup/teardown)
- `asyncio`: Async task creation
- `FastAPI`: Main web framework
- `peer_router`: Routes from `api/peer_routes.py`
- `cleanup_inactive_peers`: Background task from `tasks/peer_cleanup.py`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):

    task = asyncio.create_task(
        cleanup_inactive_peers()
    )

    yield

    task.cancel()
```

Lines 8-18: Lifespan Context Manager
- `@asynccontextmanager` decorator allows this function to handle app startup and shutdown
- On startup (before `yield`):
  - Create async task running `cleanup_inactive_peers()` coroutine
  - This task runs in background continuously
  - `yield` allows app to start serving requests
- On shutdown (after `yield`):
  - `task.cancel()` stops the cleanup task

Why this approach? FastAPI's lifespan parameter replaces older startup/shutdown events; it provides one unified context manager for setup/teardown, ensuring cleanup always runs even on errors.

```python
app = FastAPI(
    title="SwarmCDN Tracker",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(peer_router)
```

Lines 20-28: App Creation and Configuration
- `FastAPI(...)` constructor
  - `title`: Shown in OpenAPI docs at /docs
  - `version`: API version
  - `lifespan=lifespan`: Attach our lifecycle manager
- `include_router(peer_router)`: Register all routes from `peer_router` (routes defined in `api/peer_routes.py`)

```python
@app.get("/")
def root():
    return {
        "service": "SwarmCDN Tracker",
        "status": "running"
    }
```

Lines 30-35: Health Check Endpoint
- Simple GET `/` endpoint
- Returns JSON object indicating service is running
- Used for liveness probes in production Kubernetes deployments

**Startup Sequence**:
1. FastAPI app created
2. Lifespan manager starts: cleanup task created and starts running
3. Server begins accepting requests
4. Routes in `peer_routes.py` become available

**Shutdown Sequence**:
1. Server receives shutdown signal
2. Lifespan manager's after-yield code executes
3. Cleanup task is cancelled
4. All pending requests are finished
5. Process exits

**Thread Safety**: FastAPI/Starlette handle concurrency via asyncio; the cleanup task and HTTP handlers run in same event loop without explicit locking.

---

### app/db/database.py

**Purpose**: SQLAlchemy engine and session factory initialization

**Complete Code**:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
```

**Explanation**:

Line 8: `load_dotenv()` 
- Reads `.env` file and loads variables into `os.environ`
- Enables connection string from environment

Line 10: `DATABASE_URL = os.getenv("DATABASE_URL")`
- Loads database connection string from environment
- Example: `"sqlite:///./test.db"` or `"postgresql://user:pass@host/db"`

Lines 12-15: `engine = create_engine(...)`
- Creates SQLAlchemy engine (connection pool)
- `pool_pre_ping=True`: Before using a connection, run a SELECT 1 to verify it's still alive. Reconnects if stale.
- This prevents "connection lost" errors in long-running apps

Lines 17-21: `SessionLocal = sessionmaker(...)`
- Factory for creating database sessions
- `autocommit=False`: Changes aren't committed until explicitly calling `session.commit()`
- `autoflush=False`: Objects aren't automatically flushed to database
- `bind=engine`: Sessions use our engine

**Usage Pattern**:
```python
# Get a session
db = SessionLocal()
try:
    # Do operations
    peer = db.query(Peer).first()
finally:
    db.close()
```

---

### app/db/base.py

**Complete Code**:
```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

**Explanation**:
- Defines the base class for all ORM models
- In SQLAlchemy 2.0+, `DeclarativeBase` replaces `declarative_base()` function
- All database models (like `Peer`) inherit from this `Base`
- When `Base.metadata.create_all(engine)` is called, all inherited models' tables are created

**Why separate file?** Avoids circular imports: models import `Base` from here, and here imports only from sqlalchemy.

---

### app/models/peer.py

**Purpose**: SQLAlchemy ORM model representing the `peers` database table

**Complete Code**:

```python
from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, 
    Integer, String, func
)

from app.db.base import Base


class Peer(Base):
    __tablename__ = "peers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    peer_id = Column(String(100), unique=True, nullable=False)

    installation_id = Column(String(100), unique=True, nullable=False)

    ip_address = Column(String(45), nullable=False)

    port = Column(Integer, nullable=False)

    status = Column(String(10), nullable=False, default="Online")

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    last_seen = Column(DateTime, server_default=func.now(), nullable=False)
```

**Field Explanations**:

- `__tablename__ = "peers"`: Maps this class to the `peers` table
- `id`: Primary key, auto-incremented by database
- `peer_id`: Unique peer identifier, cannot be NULL, max 100 chars
- `installation_id`: Unique instance tracker, cannot be NULL
- `ip_address`: IPv4/IPv6 address, max 45 chars (for IPv6), nullable=False
- `port`: TCP port number
- `status`: "online" or "offline", defaults to "Online" (note: case inconsistency; should be lowercase)
- `created_at`: Timestamp when peer first registered; `server_default=func.now()` means database server sets the value (not Python), ensuring consistency across timezones
- `last_seen`: Timestamp of last heartbeat; also set by server

**Design Notes**:
- `server_default=func.now()`: Good because database is source of truth for time; avoids clock skew issues
- `String(45)` for IP: Sufficient for IPv6 full notation (39 chars max) + margin
- Constraints (`unique=True`, `nullable=False`) are enforced at database level, providing data integrity

**ORM Capabilities**:
Once this model is defined, SQLAlchemy enables:
```python
# Create
peer = Peer(peer_id="peer_abc", installation_id="xyz", 
            ip_address="192.168.1.1", port=5000, status="online")
db.add(peer)
db.commit()

# Read
peer = db.query(Peer).filter(Peer.peer_id == "peer_abc").first()

# Update
peer.status = "offline"
db.commit()

# Delete
db.delete(peer)
db.commit()
```

---

### app/schemas/peer_schema.py

**Complete Code**:
```python
from pydantic import BaseModel

class PeerRegistrationRequest(BaseModel):
    peer_id: str
    port: int
    installation_id: str
```

**Explanation**:
- Pydantic `BaseModel` provides automatic validation for incoming requests
- FastAPI automatically calls this validator on request payloads
- Fields are required (not `Optional`) unless marked otherwise
- Type hints (`str`, `int`) are validated; wrong types return HTTP 422 Unprocessable Entity

**Example Request**:
```json
{
    "peer_id": "peer_586b735ad8d9",
    "port": 5000,
    "installation_id": "fb15af0f49e84a10bad2ec5adcfebe31"
}
```

**Validation Behavior**: If request is missing `peer_id` or has `port` as a string (not int), Pydantic rejects it and FastAPI returns:
```json
{
    "detail": [
        {
            "type": "missing",
            "loc": ["body", "peer_id"],
            "msg": "Field required"
        }
    ]
}
```

---

### app/schemas/heartbeat_schema.py

**Complete Code**:
```python
from pydantic import BaseModel

class HeartbeatRequest(BaseModel):
    peer_id: str
```

**Explanation**:
- Simple schema: only `peer_id` required
- Used to validate `/heartbeat` POST requests

---

### app/repositories/peer_repository.py (Complete Breakdown)

**Purpose**: Data access layer; all database queries for peers

**Method 1: `get_by_peer_id`**
```python
@staticmethod
def get_by_peer_id(db: Session, peer_id: str):
    return (
        db.query(Peer)
        .filter(Peer.peer_id == peer_id)
        .first()
    )
```
- Query the `peers` table for a single record
- Filter by `peer_id` column
- `.first()` returns first match or `None`
- Used when registering (check if peer exists) and heartbeat (update existing peer)

**Method 2: `get_by_installation_id`**
```python
@staticmethod
def get_by_installation_id(db: Session, installation_id: str):
    return (
        db.query(Peer)
        .filter(Peer.installation_id == installation_id)
        .first()
    )
```
- Similar to above but queries by `installation_id`
- Used to detect if this installation was previously registered with a different `peer_id`

**Method 3: `create_peer`**
```python
@staticmethod
def create_peer(db: Session, peer: Peer):
    db.add(peer)
    db.commit()
    db.refresh(peer)
    return peer
```
- `db.add(peer)`: Mark object for insertion
- `db.commit()`: Execute INSERT to database
- `db.refresh(peer)`: Re-fetch from database to populate auto-generated fields (like `id`, `created_at` timestamps set by database)
- Returns refreshed object with all fields populated

**Method 4: `update_peer`**
```python
@staticmethod
def update_peer(db: Session, peer: Peer):
    db.commit()
    db.refresh(peer)
    return peer
```
- Called after modifying a peer object
- `db.commit()`: Flush changes to database
- `db.refresh(peer)`: Re-fetch to ensure `last_seen` timestamp is current
- Returns updated object

**Method 5: `get_all_peers`**
```python
@staticmethod
def get_all_peers(db: Session):
    return db.query(Peer).all()
```
- Retrieve all peers regardless of status
- Returns list of all `Peer` objects (may be large if thousands of peers)

**Method 6: `mark_inactive_peers`**
```python
@staticmethod
def mark_inactive_peers(db: Session):
    timeout = datetime.utcnow() - timedelta(seconds=60)
    
    (
        db.query(Peer)
        .filter(
            Peer.status == "online",
            Peer.last_seen < timeout
        ) 
        .update(
            {"status": "offline"},
            synchronize_session=False
        )
    )
    
    db.commit()
```

**Detailed explanation**:
- Line 1: Calculate cutoff time = now - 60 seconds
- Lines 3-7: Query for peers where:
  - `status == "online"` AND
  - `last_seen < timeout` (haven't received heartbeat for 60+ seconds)
- Line 8-11: Bulk UPDATE these peers' status to "offline"
  - `synchronize_session=False`: Don't update Python objects in memory; just update database
  - This is efficient for bulk operations
- Line 13: Commit changes
- Note: Called every 30 seconds by cleanup task; after 120s without heartbeat, peer marked offline

---

### app/services/peer_service.py (Complete Breakdown)

**Purpose**: Business logic for peer management

**Method 1: `register_peer`**

```python
@staticmethod
def register_peer(db: Session, peer_id: str, ip_address: str, 
                  port: int, installation_id: str):
    
    peer = PeerRepository.get_by_peer_id(db, peer_id)
    now = datetime.utcnow()
    
    existing_installation = (
        PeerRepository.get_by_installation_id(db, installation_id)
    )
    
    # Conflict Check 1: Same installation, different peer_id
    if (
        existing_installation is not None
        and
        (
            peer is None
            or
            peer.installation_id != installation_id
        )
    ):
        raise HTTPException(
            status_code=403,
            detail="Installation ID already exists with a different peer ID"
        )
    
    # New peer registration
    if peer is None:
        peer = Peer(
            peer_id=peer_id,
            installation_id=installation_id,
            ip_address=ip_address,
            port=port,
            status="online",
            last_seen=now
        )
        return PeerRepository.create_peer(db, peer)
    
    # Conflict Check 2: Same peer_id, different installation_id
    if peer.installation_id != installation_id:
        raise HTTPException(
            status_code=403,
            detail="Peer ID already exists with a different installation ID"
        )
    
    # Update existing peer
    peer.ip_address = ip_address
    peer.port = port
    peer.status = "online"
    peer.last_seen = now
    
    return PeerRepository.update_peer(db, peer)
```

**Explanation of Logic**:

**Scenario 1**: Fresh peer registration (neither `peer_id` nor `installation_id` exist)
- Check passes, new `Peer` object created and inserted
- Status set to "online"

**Scenario 2**: Peer restarts on same machine (same `peer_id`, same `installation_id`)
- Existing peer found by `peer_id`
- Installation ID matches → update IP/port and mark online
- This is the normal re-registration case

**Scenario 3**: Same installation, different `peer_id` (user changes peer_id config)
- `existing_installation` not None (found by installation_id)
- But `peer` is None or has different installation_id
- Raises 403 Forbidden
- Prevents one machine from masquerading as multiple peers

**Scenario 4**: Peer ID collision with different installation (malicious or configuration error)
- `peer_id` exists but with different`installation_id`
- Raises 403 Forbidden
- Prevents two machines from claiming same peer_id

**Why Conflict Detection?**
- Ensures peer identity is tied to installation, not just a user-configurable string
- Prevents duplicate registrations that could cause network inconsistencies

**Method 2: `get_all_peers`**
```python
@staticmethod
def get_all_peers(db: Session):
    return PeerRepository.get_all_peers(db)
```
- Pass-through to repository
- Returns list of all `Peer` objects (converted to JSON by FastAPI)

**Method 3: `heartbeat`**
```python
@staticmethod
def heartbeat(db: Session, peer_id: str):
    peer = PeerRepository.get_by_peer_id(db, peer_id)
    
    if peer is None:
        return None  # Peer not found, caller returns 404-like response
    
    peer.status = "online"
    peer.last_seen = datetime.utcnow()
    
    return PeerRepository.update_peer(db, peer)
```
- Look up peer by ID
- If not found, return `None` (caller decides response)
- Update `last_seen` to current time and ensure status is "online"
- This keeps peer from being marked offline

**Method 4: `mark_inactive_peers`**
```python
@staticmethod
def mark_inactive_peers(db: Session):
    PeerRepository.mark_inactive_peers(db)
```
- Simple delegation to repository; marks peers without recent heartbeats as offline

---

### app/api/peer_routes.py (Complete Endpoints)

**Endpoint 1: POST `/register-peer`**

```python
@router.post("/register-peer")
def register_peer(
    peer: PeerRegistrationRequest,
    request: Request,
    db: Session = Depends(get_db)
):

    peer_data = PeerService.register_peer(
        db=db,
        peer_id=peer.peer_id,
        installation_id=peer.installation_id,
        ip_address=request.client.host,
        port=peer.port
    )

    return {
        "message": "Peer registered successfully",
        "peer": peer_data
    }
```

**Explanation**:
- `peer: PeerRegistrationRequest`: FastAPI validates incoming JSON against schema
- `request: Request`: FastAPI Request object giving access to client IP
- `db: Session = Depends(get_db)`: Dependency injection; `get_db()` is called to provide a session
- `request.client.host`: Extract IP address of requester
- `PeerService.register_peer()`: Call business logic
- Returns JSON with message and peer data

**Flow**:
1. HTTP POST `/register-peer` with body `{"peer_id": "...", "port": 5000, "installation_id": "..."}`
2. FastAPI routes to this function
3. Pydantic validates request body
4. `get_db()` provides database session
5. Peer registered/updated in database
6. Response sent back as JSON

**Error Handling**: 
- If `PeerService.register_peer()` raises `HTTPException` (e.g., 403 conflict), FastAPI catches it and returns appropriate HTTP status

**Endpoint 2: GET `/peers`**

```python
@router.get("/peers")
def get_peers(db: Session = Depends(get_db)):
    return PeerService.get_all_peers(db)
```

**Explanation**:
- Simple GET endpoint; no request body needed
- Returns list of all `Peer` objects
- FastAPI automatically converts to JSON using Pydantic serialization

**Response Example**:
```json
[
    {
        "id": 1,
        "peer_id": "peer_586b735ad8d9",
        "installation_id": "fb15af0f49e84a10bad2ec5adcfebe31",
        "ip_address": "192.168.1.100",
        "port": 5000,
        "status": "online",
        "created_at": "2024-01-15T10:00:00",
        "last_seen": "2024-01-15T10:05:00"
    },
    ...
]
```

**Endpoint 3: POST `/heartbeat`**

```python
@router.post("/heartbeat")
def heartbeat(
    heartbeat: HeartbeatRequest,
    db: Session = Depends(get_db)
):

    peer = PeerService.heartbeat(db, heartbeat.peer_id)

    if peer is None:
        return {
            "message": "Peer not found"
        }

    return {
        "message": "Heartbeat received"
    }
```

**Explanation**:
- `heartbeat: HeartbeatRequest`: Validates `{"peer_id": "..."}`
- `PeerService.heartbeat()`: Updates `last_seen` and status
- If peer not found, return message (doesn't return 404, just body message)
- Success returns "Heartbeat received"

**Design Note**: The response is just a message, not peer data, because heartbeats are fire-and-forget operations; peers don't need confirmation details.

---

### app/tasks/peer_cleanup.py

**Purpose**: Background task marking inactive peers as offline

**Complete Code and Explanation**:

```python
import asyncio

from app.db.database import SessionLocal
from app.services.peer_service import PeerService


async def cleanup_inactive_peers():

    while True:

        db = SessionLocal()

        try:
            PeerService.mark_inactive_peers(db)

        finally:
            db.close()

        await asyncio.sleep(30)
```

**Line-by-line**:
- Line 1: Import asyncio for async/await
- Line 3-4: Import session factory and service
- Line 7: Define async coroutine
- Line 8: Infinite loop (runs until task is cancelled)
- Line 10: Create new database session for this iteration
- Line 12: Try block for safe operation
- Line 13: Call service to mark inactive peers offline (this runs the bulk UPDATE query)
- Line 15: Finally block ensures cleanup
- Line 16: Close database session
- Line 18: Await 30 seconds before next iteration

**Execution Model**:
- Runs concurrently with HTTP request handlers in the same asyncio event loop
- Every 30 seconds, peers with `last_seen` older than 60 seconds are marked offline
- If a peer goes offline for 60 seconds without heartbeat, it's marked offline
- If it sends heartbeat again, it's marked back online

**Why Separate Task?**
- HTTP handlers shouldn't be blocked by database operations
- Background cleanup doesn't interfere with request latency
- Continuous monitoring of peer health

---

### app/db/dependencies.py

**Complete Code**:
```python
from app.db.database import SessionLocal


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
```

**Explanation**:
- `get_db()` is a dependency for FastAPI routes
- Syntax `yield` makes this a generator; FastAPI uses it for setup/teardown
- Before route handler runs: create session
- After route handler completes (or raises error): close session in finally
- This ensures every request gets a fresh session and cleanup happens automatically

**FastAPI Integration**:
```python
@router.get("/peers")
def get_peers(db: Session = Depends(get_db)):
    # db is automatically provided
    return PeerService.get_all_peers(db)
```

---

### requirements.txt

**Dependencies**:
```
fastapi==0.136.3         # Web framework
uvicorn==0.49.0          # ASGI server
pydantic==2.13.4         # Request validation  
sqlalchemy               # (implicit via ORM)
starlette==1.2.1         # Async web toolkit
```

**Why these?**:
- `fastapi`: Modern, async-first, automatic OpenAPI docs
- `uvicorn`: Production-grade async server
- `pydantic`: Schema validation and serialization
- `starlette`: Underlying web platform for FastAPI

---

## 7 API Endpoints (Complete Reference)

### Endpoint: POST /register-peer

**Path**: `POST /register-peer`

**Request Schema**:
```json
{
    "peer_id": "peer_586b735ad8d9",
    "port": 5000,
    "installation_id": "fb15af0f49e84a10bad2ec5adcfebe31"
}
```

**Request Processing**:
1. Pydantic validates: `peer_id` (str), `port` (int), `installation_id` (str)
2. FastAPI extracts `request.client.host` for IP address
3. Service layer checks conflicts and registers/updates

**Success Response (201 Created - implied)**:
```json
{
    "message": "Peer registered successfully",
    "peer": {
        "id": 1,
        "peer_id": "peer_586b735ad8d9",
        "installation_id": "fb15af0f49e84a10bad2ec5adcfebe31",
        "ip_address": "192.168.1.100",
        "port": 5000,
        "status": "online",
        "created_at": "2024-01-15T10:00:00",
        "last_seen": "2024-01-15T10:00:00"
    }
}
```

**Error Responses**:

**403 Forbidden - Installation Conflict**:
```json
{
    "detail": "Installation ID already exists with a different peer ID"
}
```
Occurs when: Same installation ID registered with different peer_id

**403 Forbidden - Peer ID Conflict**:
```json
{
    "detail": "Peer ID already exists with a different installation ID"
}
```
Occurs when: Same peer_id but different installation_id

**422 Unprocessable Entity** (implicit from Pydantic):
```json
{
    "detail": [
        {
            "loc": ["body", "peer_id"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```
Occurs when: Required fields missing or wrong types

### Endpoint: GET /peers

**Path**: `GET /peers`

**Request**: No body required

**Success Response (200 OK)**:
```json
[
    {
        "id": 1,
        "peer_id": "peer_586b735ad8d9",
        "installation_id": "fb15af0f49e84a10bad2ec5adcfebe31",
        "ip_address": "192.168.1.100",
        "port": 5000,
        "status": "online",
        "created_at": "2024-01-15T10:00:00",
        "last_seen": "2024-01-15T10:05:00"
    },
    {
        "id": 2,
        "peer_id": "peer_xyz789",
        "installation_id": "abc123def456",
        "ip_address": "192.168.1.101",
        "port": 5001,
        "status": "offline",
        "created_at": "2024-01-15T09:00:00",
        "last_seen": "2024-01-15T09:30:00"
    }
]
```

**Notes**:
- Returns all peers (including offline)
- Peers filter this list locally (remove self, filter by status, etc.)
- If no peers registered, returns empty list `[]`

### Endpoint: POST /heartbeat

**Path**: `POST /heartbeat`

**Request Schema**:
```json
{
    "peer_id": "peer_586b735ad8d9"
}
```

**Success Response (200 OK)**:
```json
{
    "message": "Heartbeat received"
}
```

**Failure Response (200 OK - no distinction)**:
```json
{
    "message": "Peer not found"
}
```

Note: The endpoint returns 200 even if peer not found (design choice; could be 404). Caller should test message content.

**Behavior**:
- Updates `last_seen` to current timestamp
- Sets `status = "online"`
- Prevents peer from being marked offline by cleanup task

---

## 8 Data Models

### Peer ORM Model

**Full Model Definition**:
```python
class Peer(Base):
    __tablename__ = "peers"
    
    id: BigInteger = Column(BigInteger, primary_key=True, autoincrement=True)
    peer_id: str = Column(String(100), unique=True, nullable=False)
    installation_id: str = Column(String(100), unique=True, nullable=False)
    ip_address: str = Column(String(45), nullable=False)
    port: int = Column(Integer, nullable=False)
    status: str = Column(String(10), nullable=False, default="online")
    created_at: DateTime = Column(DateTime, server_default=func.now())
    last_seen: DateTime = Column(DateTime, server_default=func.now())
```

**Lifecycle Management**:

**On Creation**:
- `id`: Auto-generated by database
- `created_at`: Set by database to current time
- `last_seen`: Set to current time
- `status`: Defaults to "online"

**On Heartbeat**:
- `last_seen`: Updated to current time
- `status`: Explicitly set to "online"

**On Cleanup (every 30s)**:
- `status`: Changed to "offline" if `last_seen > 60 seconds old`

**Design Pattern**: Peer objects are stateful; the database is the source of truth. Python doesn't hold peer state between requests; every operation queries fresh from database.

### Pydantic Request Models

**PeerRegistrationRequest**:
```python
class PeerRegistrationRequest(BaseModel):
    peer_id: str        # User-assigned peer identifier
    port: int           # TCP port where peer listens
    installation_id: str # Unique per installation
```

**HeartbeatRequest**:
```python
class HeartbeatRequest(BaseModel):
    peer_id: str        # Which peer this heartbeat is from
```

---

## 9 Service Layer

### PeerService Class

**Method Signatures**:
```python
class PeerService:
    @staticmethod
    def register_peer(db: Session, peer_id: str, ip_address: str, 
                      port: int, installation_id: str) -> Peer:
        """Register new peer or update existing one"""
    
    @staticmethod
    def get_all_peers(db: Session) -> List[Peer]:
        """Get all peers (online and offline)"""
    
    @staticmethod
    def heartbeat(db: Session, peer_id: str) -> Optional[Peer]:
        """Update last_seen for a peer"""
    
    @staticmethod
    def mark_inactive_peers(db: Session) -> None:
        """Mark peers without recent heartbeats as offline"""
```

**Responsibilities**:
1. **Conflict Detection**: Prevent duplicate peer IDs and installation IDs
2. **State Management**: Transition peers between online/offline
3. **Data Validation**: Ensure peer data is consistent
4. **Orchestration**: Coordinate between repositories and business logic

**Invariants Maintained**:
- One `peer_id` uniquely identifies a peer
- One `installation_id` uniquely identifies a machine
- Peer can only be registered if both peer_id and installation_id are unique
- Status is either "online" or "offline"
- `last_seen` is never in the future
- `created_at` never changes after initial creation

---

## 10 Repository Layer

### PeerRepository Class

**Purpose**: Abstract all database interactions

**Methods**:
1. **get_by_peer_id(db, peer_id)**: Single record lookup by peer ID
2. **get_by_installation_id(db, id)**: Single record lookup by installation ID
3. **create_peer(db, peer)**: Insert new peer, return with auto-generated fields
4. **update_peer(db, peer)**: Persist peer changes
5. **get_all_peers(db)**: Fetch all peers in database
6. **mark_inactive_peers(db)**: Bulk UPDATE peers based on timestamp

**Design Benefits**:
- Database queries isolated in one class
- Easy to mock for testing
- Changes to queries don't scatter across codebase
- SQL can be optimized independently from business logic

**Limitations of Current Implementation**:
- No pagination (get_all_peers loads all records into memory)
- No filtering (peers must filter results themselves)
- Bulk update doesn't handle partial failures

---

## 11 Background Tasks

### Cleanup Task Execution Model

**Trigger**: Runs every 30 seconds in background (continuous)

**Operation**:
```
Every 30 seconds:
  Find all peers where status="online" AND last_seen < NOW - 60 seconds
  Set their status="offline"
  Commit to database
  Wait 30 seconds
```

**Timeout Calculation**:
```
Current Time: 2024-01-15 10:05:00
Threshold: NOW - 60 seconds = 2024-01-15 10:04:00
Mark offline if: last_seen < 2024-01-15 10:04:00
```

**Example Timeline**:
```
10:00:00 - Peer X registers, last_seen=10:00:00, status=online
10:00:30 - Cleanup tick, threshold=9:59:30, X.last_seen > threshold, no change
10:01:00 - Cleanup tick, threshold=10:00:00, X.last_seen == threshold, no change
10:01:30 - Cleanup tick, threshold=10:00:30, X.last_seen < threshold, mark OFFLINE
```

**Concurrency Model**:
- Runs in same asyncio event loop as HTTP handlers
- Cleanup task doesn't block requests
- Multiple requests and cleanup operations interleave

**Failure Handling**:
- If database error during cleanup, exception caught in try/finally
- Session closed even on error
- Next cleanup attempt runs after 30 seconds

---

## 12 Configuration & Startup

### Environment Variables

```bash
DATABASE_URL=sqlite:///./test.db
# or
DATABASE_URL=postgresql://user:password@localhost/meshcdn
```

### Startup Sequence

```
1. Python loads main.py
2. FastAPI() app created
3. Lifespan context manager attached
4. Routes included (peer_router)
5. Server starts listening on 0.0.0.0:8000 (default Uvicorn)
6. __enter__ of lifespan executes:
   - cleanup_inactive_peers() coroutine created
   - Background task starts running
7. Server ready to accept requests
8. HTTP requests routed to handlers
9. Every 30 seconds: cleanup task marks inactive peers offline
10. On shutdown signal:
    - __exit__ of lifespan executes
    - cleanup task cancelled
    - all sessions closed
    - process exits
```

---

## 13 Data Flow

### Registration Flow

```
PEER        →         TRACKER
    POST /register-peer
          {peer_id, port, installation_id}
              ↓
        [FastAPI Router]
              ↓
        [Pydantic validates]
              ↓
        [Extract request.client.host]
              ↓
        [PeerService.register_peer()]
              ↓
        Check conflicts:
        - Query Peer by peer_id
        - Query Peer by installation_id
        - Validate no duplicate across dimensions
              ↓
        If new: INSERT Peer
        If update: UPDATE Peer
              ↓
        Commit to database
              ↓
        Return Peer with {id, status=online, created_at, last_seen}
              ↓
        Response: 200 OK
    ← {message, peer}
```

### Heartbeat Flow

```
PEER        →         TRACKER
    POST /heartbeat
          {peer_id}
              ↓
        [FastAPI Router]
              ↓
        [Pydantic validates]
              ↓
        [PeerService.heartbeat()]
              ↓
        Query Peer by peer_id
              ↓
        If found:
          - Set last_seen = NOW
          - Set status = "online"
          - UPDATE peer
          - Commit
        Else:
          - Return None
              ↓
        Response: 200 OK
    ← {message: "Heartbeat received|Peer not found"}
```

### Discovery Flow

```
PEER        →         TRACKER
    GET /peers
              ↓
        [FastAPI Router]
              ↓
        [PeerService.get_all_peers()]
              ↓
        SELECT * FROM peers
              ↓
        Return all Peer objects
              ↓
        [FastAPI serializes to JSON]
              ↓
        Response: 200 OK
    ← [Peer1, Peer2, ..., PeerN]
              ↓
        [Peer filters list]
        - Remove self
        - Filter by status=online if desired
        - Extract {ip, port} for connections
```

---

## 14 Sequence Diagrams

### Peer Lifecycle

```
Peer Instance                Database              Background Task
      │                         │                        │
      │  register_peer()        │                        │
      ├────────────────────────>│                        │
      │  INSERT INTO peers      │                        │
      │  status="online"        │                        │
      │                         │                        │
      │                         │ (every 30s)            │
      │                         │<──────────────────────>│
      │                         │ Check inactive peers   │
      │ heartbeat()             │                        │
      ├────────────────────────>│                        │
      │ UPDATE last_seen        │                        │
      │ status="online"         │                        │
      │                         │                        │
      │                         │ (60s passes)           │
      │ [No heartbeat]          │                        │
      │                         │                        │
      │                         │ (cleanup runs again)   │
      │                         │<──────────────────────>│
      │                         │ last_seen > 60s,       │
      │                         │ status="offline"       │
      │                         │                        │
      │ heartbeat()             │                        │
      ├────────────────────────>│                        │
      │ UPDATE last_seen        │                        │
      │ status="online"         │                        │
      │                         │                        │
```

### Conflict Resolution

```
Peer Machine                 Database
      │
      │  registration 1:
      │  peer_id="A", install_id="X", port=5000
      ├────────────────────────>
      │  Success: Inserted
      │
      │  restart, config changed:
      │  peer_id="B", install_id="X", port=5001
      ├────────────────────────>
      │  ERROR 403:
      │  "Installation ID already exists with different peer ID"
      │  [Prevents identity confusion]
      │
      │  another peer tries:
      │  peer_id="A", install_id="Y", port=5000
      ├────────────────────────>
      │  ERROR 403:
      │  "Peer ID already exists with different installation ID"
      │  [Prevents spoofing]
```

---

## 15 Design Decisions

### Why FastAPI?

**Decision**: Use FastAPI instead of Flask, Django, or async libraries

**Rationale**:
1. **Built-in async**: All handlers are async by default; no GIL limitation
2. **Automatic validation**: Pydantic integration prevents request parsing bugs
3. **Documentation**: Automatic OpenAPI schema generation at /docs
4. **Performance**: Low overhead; among fastest Python web frameworks
5. **Modern**: Type hints throughout; IDE support excellent

**Tradeoff**: Slightly steeper learning curve than Flask; less mature ecosystem than Django

### Why SQLAlchemy ORM?

**Decision**: Use SQLAlchemy ORM instead of raw SQL or lightweight libraries like SQLite3

**Rationale**:
1. **Database portability**: Switch from SQLite to PostgreSQL with one config change
2. **Type safety**: Python types are enforced; schema validation
3. **Relationship support**: Future enhancement: foreign keys to file metadata (if tracker stores file info)
4. **Built-in migrations**: Can use Alembic for schema versioning
5. **Query abstraction**: Complex queries are expressed in Python, not SQL strings

**Tradeoff**: Slight overhead vs. raw SQL; less control over query optimization

### Why Centralized Tracker?

**Decision**: Single tracker server instead of DHT or distributed peer discovery

**Rationale (Current)**:
1. **Simplicity**: Easier to implement, debug, understand
2. **Consistency**: Single source of truth for peer registry
3. **Fast lookups**: No gossip protocol overhead
4. **Easy monitoring**: Centralized logs for debugging

**Future**: As network scales, could transition to:
- Multiple tracker instances with replication
- Distributed hash table (DHT) for decentralization
- Hybrid: Bootstrap via tracker, then use DHT for resilience

### Why Status=Offline Instead of Delete?

**Decision**: Mark peers offline rather than deleting records

**Rationale**:
1. **Audit trail**: Preserves history of peer activity
2. **Graceful degradation**: Peers reappear after heartbeat; no data loss
3. **Statistics**: Track peer uptime, network churn
4. **Debugging**: Can query historical peer data

**Data retention**: Indefinite (could add TTL in future: delete offline peers after 7 days)

### Why 60-second Heartbeat Timeout?

**Decision**: Mark peers offline if no heartbeat for 60 seconds, check every 30 seconds

**Rationale**:
1. **Responsive**: Detects offline peers within ~90 seconds (30s check + 60s grace)
2. **Tolerant**: Allows for network delays; not too aggressive
3. **Low overhead**: 30-second interval doesn't generate heavy database load
4. **Configurable**: Easy to adjust if deployment requirements change

**Alternative considered**:
- 30-second timeout: More responsive but less tolerant of network hiccups
- 120-second timeout: More tolerant but slower to detect failures

### Why Bulk UPDATE Instead of Loop?

**Decision**: Mark inactive peers in single SQL UPDATE, not loop over records

**SQL approach**:
```sql
UPDATE peers 
SET status = 'offline' 
WHERE status = 'online' AND last_seen < NOW - INTERVAL 60 SECOND
```

**Rationale**:
1. **Efficiency**: Single database round-trip vs. N round-trips (where N = inactive peer count)
2. **Transaction consistency**: Atomically updates all peers; no partial updates
3. **Scalability**: Linear in database, not in Python process
4. **Minimal locking**: One lock (on `peers` table) vs. many (per-record)

---

## 16 Error Handling

### HTTP Error Responses

#### 403 Forbidden - Installation Conflict

**Scenario**: Same installation tries to register with different peer_id

**Response Body**:
```json
{
    "detail": "Installation ID already exists with a different peer ID"
}
```

**Handling in Peer Code**:
```python
try:
    register()
except HTTPException as e:
    if e.status_code == 403:
        # Prevent dual registration
        log("Installation conflict: is another instance running?")
        sys.exit(1)
```

#### 403 Forbidden - Peer ID Conflict

**Scenario**: Another peer already claimed this peer_id

**Response Body**:
```json
{
    "detail": "Peer ID already exists with a different installation ID"
}
```

**Cause**: Usually indicates configuration error or stale database

#### 404 Not Found (Implicit) - Heartbeat for Unknown Peer

**Scenario**: Peer calls /heartbeat but peer_id is not in database

**Response Body**:
```json
{
    "message": "Peer not found"
}
```

**Note**: Tracker returns 200 OK even if peer not found (design choice; could return 404)

#### 422 Unprocessable Entity - Validation Error

**Scenario**: Invalid request body (missing field, wrong type)

**Example**: Port is a string instead of integer

**Response Body**:
```json
{
    "detail": [
        {
            "loc": ["body", "port"],
            "msg": "value is not a valid integer",
            "type": "type_error.integer"
        }
    ]
}
```

### Database Error Handling

#### Connection Failures

**Scenario**: Database server is down

**Current Handling**:
```python
try:
    peer = PeerRepository.get_by_peer_id(db, peer_id)
except DatabaseException:
    # No explicit handling; exception propagates
    # FastAPI returns 500 Internal Server Error
```

**Improvement (future)**: Implement connection pooling with retries

#### Session Cleanup

**Invariant**: Database session is always closed

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Runs even if exception occurs
```

---

## 17 Performance Considerations

### Scalability Limits (Single Instance)

**Database**: SQLite (embedded) vs. PostgreSQL (separate server)

| Component | Limit | Bottleneck |
|-----------|-------|-----------|
| Peers in registry | ~100K | RAM (all loaded into memory during /peers) |
| /register-peer throughput | ~1000 req/s | Write concurrency (SQLite locks on write) |
| /peers throughput | ~10K req/s | Network I/O (serializing large lists) |
| Cleanup task overhead | ~10ms per run | Query execution time (indexes matter) |

### Optimization Strategies

#### 1. Paginate /peers Endpoint

**Current**: Returns all peers
```python
@router.get("/peers")
def get_peers(db: Session):
    return PeerService.get_all_peers(db)  # All in one response
```

**Optimized**: Return page of 100 peers
```python
@router.get("/peers")
def get_peers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Peer).offset(skip).limit(limit).all()
```

**Benefit**: Reduces memory footprint and network bandwidth

#### 2. Filter /peers by Status

**Current**: Peers return all records and filter locally

**Optimized**: 
```python
@router.get("/peers")
def get_peers(db: Session, status: str = "online"):
    return db.query(Peer).filter(Peer.status == status).all()
```

**Benefit**: Reduces response size and network I/O

#### 3. Add Index on (status, last_seen)

**Current**: Cleanup query scans all peers

**SQL**:
```sql
CREATE INDEX idx_status_last_seen ON peers (status, last_seen);
```

**Benefit**: Cleanup query uses index; execution time drops from O(N) to O(log N)

#### 4. Use PostgreSQL (not SQLite)

**SQLite**: Single writer, concurrent readers (thread locking)

**PostgreSQL**: True concurrent writes, connection pooling

**Benefit**: Higher throughput under load

### Memory Profile

**Per Peer in Memory**:
- Peer object: ~5KB (strings, timestamps, integers)
- In-flight responses: 100 peers/response × 5KB = 500KB per /peers call

**Total Memory** (1000 peers):
- Database connection: 1MB
- Cached in memory: ~5MB
- Per request: 500KB (temporary)

---

## 18 Security Analysis

### Authentication & Authorization

**Current State**: None

**Vulnerability**: Any peer can:
- Register with any ID
- Claim any installation_id
- Spoof peer IP addresses (partially mitigated: tracker extracts IP from socket)
- Spam /heartbeat requests

**Mitigation Strategies** (future):
1. **API Key**: Require Authorization header
2. **mTLS**: Mutual TLS certificates for peer identity
3. **Rate limiting**: Track request rate per peer_id
4. **IP validation**: Cross-check claimed IP with socket IP

### SQL Injection

**Risk**: None (all queries use parameterized SQLAlchemy)

**Example**: Peer tries register with `peer_id = "'; DROP TABLE--"`

```python
db.query(Peer).filter(Peer.peer_id == "'; DROP TABLE--").first()
# SQLAlchemy converts to: SELECT * FROM peers WHERE peer_id = ?;DROP TABLE--'
# Single quotes escaped; treated as literal string
```

### Data Validation

**Current Validation**:
- `peer_id`: Non-empty string (length 0-100)
- `port`: Non-negative integer (0-65535)
- `installation_id`: Non-empty string (0-100)

**Missing Validation**:
- Port range (currently accepts 0-65535; should validate > 1024)
- Peer ID format (currently any string; could enforce alphanumeric)
- IP address format (currently trusts client socket; could validate)

### Network Security

**Risk**: HTTP (unencrypted)

**Exposure**: Peer registrations, heartbeats transmitted in plaintext

**Mitigation**: HTTPS with valid certificate

**Future**: mTLS for P2P connections between tracker and peers

### State Separation

**Risk**: Single tracker instance is single point of failure

**Mitigation** (future):
- Deploy multiple tracker instances
- Shared PostgreSQL with replication
- Load balancer for failover

---

## 19 Future Roadmap

### Short-term (1-3 months)

1. **Pagination for /peers**
   - Add `skip` and `limit` parameters
   - Reduces memory and network overhead
   - Peers request only needed subset

2. **Status Filtering**
   - `GET /peers?status=online` returns only online peers
   - Reduces response size

3. **Metrics Endpoint**
   - `GET /metrics`: Total peers, online/offline counts, request rates
   - Useful for monitoring and debugging

4. **Configuration File**
   - Move DATABASE_URL, timeouts, ports to config file
   - No need to rebuild Docker image for config changes

### Medium-term (3-6 months)

1. **PostgreSQL Migration**
   - Replace SQLite with PostgreSQL for production
   - Requires connection pooling and replication setup

2. **API Key Authentication**
   - Require `Authorization: Bearer <key>` header
   - Prevent unauthorized peer registrations

3. **Rate Limiting**
   - Limit requests per peer_id per second
   - Prevent heartbeat spam attacks

4. **Peer Notifications**
   - WebSocket support: Tracker can push peer list updates
   - Reduces polling overhead
   - More responsive peer discovery

### Long-term (6+ months)

1. **Distributed Tracker (DHT)**
   - Move from centralized tracker to DHT
   - Each peer participates in peer discovery
   - No single point of failure

2. **Peer Reputation**
   - Track peer quality (success rate, latency, uptime)
   - Return ranked peer lists
   - Prefer high-quality peers for downloads

3. **File Discovery**
   - Tracker learns what files peers have (index)
   - Query tracker for peers containing specific file
   - Faster file discovery without asking every peer

4. **Analytics**
   - Track network topology
   - Measure peer churn (registration/departure rate)
   - Identify network bottlenecks

---

## 20 Developer Guide

### Setting Up Development Environment

#### 1. Clone Repository
```bash
git clone <repo_url>
cd backend/tracker
```

#### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Create .env File
```bash
cat > .env << EOF
DATABASE_URL=sqlite:///./test.db
EOF
```

#### 5. Run Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag automatically restarts server when files change.

#### 6. Access OpenAPI Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Raw OpenAPI schema: http://localhost:8000/openapi.json

### Writing Tests

#### Example: Test Registration

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_peer():
    response = client.post(
        "/register-peer",
        json={
            "peer_id": "test_peer",
            "port": 5000,
            "installation_id": "test_install"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["peer"]["peer_id"] == "test_peer"
    assert data["peer"]["status"] == "online"
```

#### Example: Test Conflict Detection

```python
def test_registration_conflict():
    # First registration
    client.post(
        "/register-peer",
        json={
            "peer_id": "peer1",
            "port": 5000,
            "installation_id": "install1"
        }
    )
    
    # Second registration with same installation_id
    response = client.post(
        "/register-peer",
        json={
            "peer_id": "peer2",
            "port": 5001,
            "installation_id": "install1"  # Same!
        }
    )
    
    assert response.status_code == 403
    assert "Installation ID already exists" in response.text
```

### Adding New Endpoints

#### Example: Delete Peer Endpoint

```python
# app/api/peer_routes.py

@router.delete("/peers/{peer_id}")
def delete_peer(peer_id: str, db: Session = Depends(get_db)):
    peer = PeerRepository.get_by_peer_id(db, peer_id)
    
    if peer is None:
        raise HTTPException(
            status_code=404,
            detail=f"Peer {peer_id} not found"
        )
    
    db.delete(peer)
    db.commit()
    
    return {"message": f"Peer {peer_id} deleted"}
```

**Add to service layer**:
```python
# app/services/peer_service.py

@staticmethod
def delete_peer(db: Session, peer_id: str):
    peer = PeerRepository.get_by_peer_id(db, peer_id)
    if peer:
        db.delete(peer)
        db.commit()
    return peer
```

### Database Schema Modifications

#### Example: Add Bandwidth Field

```python
# 1. Update model
class Peer(Base):
    ...
    bandwidth_mb: int = Column(Integer, default=0)

# 2. Create migration (with Alembic)
alembic revision --autogenerate -m "Add bandwidth to peer"

# 3. Run migration
alembic upgrade head

# 4. Update schema request
class PeerRegistrationRequest(BaseModel):
    peer_id: str
    port: int
    installation_id: str
    bandwidth_mb: int = 0  # With default

# 5. Update service logic
@staticmethod
def register_peer(db, peer_id, ip_address, port, installation_id, bandwidth_mb):
    peer = Peer(
        ...,
        bandwidth_mb=bandwidth_mb
    )
```

### Deployment

#### Option 1: Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t meshcdn-tracker .
docker run -e DATABASE_URL=postgresql://... -p 8000:8000 meshcdn-tracker
```

#### Option 2: Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: meshcdn-tracker
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: tracker
        image: meshcdn-tracker:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: tracker-secrets
              key: database-url
        livenessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
```

### Debugging Tips

#### 1. Enable Debug Logging

```python
# app/main.py

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@router.post("/heartbeat")
def heartbeat(heartbeat: HeartbeatRequest, db: Session = Depends(get_db)):
    logger.debug(f"Heartbeat from {heartbeat.peer_id}")
    peer = PeerService.heartbeat(db, heartbeat.peer_id)
    logger.info(f"Peer status: {peer.status if peer else 'NOT FOUND'}")
    return {"message": "OK"}
```

#### 2. Inspect Database

```bash
# SQLite
sqlite3 test.db "SELECT * FROM peers;"

# PostgreSQL
psql $DATABASE_URL -c "SELECT * FROM peers ORDER BY last_seen DESC;"
```

#### 3. Monitor Background Task

```python
# app/tasks/peer_cleanup.py

async def cleanup_inactive_peers():
    iteration = 0
    while True:
        iteration += 1
        db = SessionLocal()
        
        try:
            print(f"[Cleanup {iteration}] Running at {datetime.utcnow()}")
            PeerService.mark_inactive_peers(db)
            print(f"[Cleanup {iteration}] Complete")
        finally:
            db.close()
        
        await asyncio.sleep(30)
```

Run server and tail terminal: see cleanup messages every 30 seconds

#### 4. Check Endpoints

```bash
# Health check
curl http://localhost:8000/

# View all peers
curl http://localhost:8000/peers

# Register peer
curl -X POST http://localhost:8000/register-peer \
  -H "Content-Type: application/json" \
  -d '{"peer_id":"test","port":5000,"installation_id":"xyz"}'

# Send heartbeat
curl -X POST http://localhost:8000/heartbeat \
  -H "Content-Type: application/json" \
  -d '{"peer_id":"test"}'
```

---

## Summary

The MeshCDN Tracker is a lightweight, purpose-built peer registry service designed to support decentralized file sharing. By centralizing peer awareness while keeping peer relationships decentralized, it achieves simplicity without sacrificing scalability for small to medium networks.

**Key Takeaways**:
- **Simple architecture**: 4 layers (API, Service, Repository, Database)
- **Lean implementation**: ~300 lines of code, minimal dependencies
- **Production-ready**: Error handling, validation, background tasks
- **Extensible**: Easy to add features (pagination, filtering, authentication)
- **Scalable roadmap**: Clear path to distributed tracker or DHT

This handbook should enable any developer to understand, modify, test, and deploy the Tracker component independently.

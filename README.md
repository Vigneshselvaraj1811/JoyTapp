# JoyTapp Backend API

Production-grade REST API built with **FastAPI**, **MongoDB (Motor)**, **JWT Authentication**, and **AWS S3**.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI (async) |
| Database | MongoDB via Motor (async driver) |
| Auth | JWT — Access + Refresh Tokens |
| File Storage | AWS S3 Pre-signed URLs |
| Password Hashing | bcrypt (passlib) |
| Validation | Pydantic v2 |
| Config | pydantic-settings + `.env` |

---

## Project Structure

```
joytapp-backend/
├── app/
│   ├── main.py                     # App factory, middleware, exception handlers
│   ├── api/
│   │   └── v1/
│   │       ├── router.py           # Central router — wires all endpoint modules
│   │       └── endpoints/
│   │           ├── auth.py         # POST /auth/register|login|refresh-token|logout
│   │           ├── users.py        # GET|PUT /users/profile, GET /users/{id}
│   │           ├── posts.py        # CRUD /posts
│   │           ├── interactions.py # /posts/{id}/like|comment|comments
│   │           └── uploads.py      # POST /uploads/presigned-url
│   ├── core/
│   │   ├── config.py               # All settings via .env
│   │   ├── security.py             # JWT encode/decode, password hashing, auth dependency
│   │   ├── dependencies.py         # FastAPI DI — service factories
│   │   └── exceptions.py           # Global HTTP exception handlers
│   ├── db/
│   │   └── mongodb.py              # Motor client, connection lifecycle, index creation
│   ├── repositories/
│   │   ├── base.py                 # Generic CRUD (find, insert, update, soft_delete)
│   │   ├── user_repository.py
│   │   ├── auth_repository.py      # Refresh token storage + revocation
│   │   ├── post_repository.py      # Pagination, filtering, soft delete
│   │   └── interaction_repository.py  # Likes (unique), paginated comments
│   ├── services/
│   │   ├── auth_service.py         # Register, login, refresh, logout logic
│   │   ├── user_service.py         # Profile management
│   │   ├── post_service.py         # Post CRUD with ownership checks
│   │   ├── interaction_service.py  # Toggle likes, add/list comments
│   │   └── upload_service.py       # S3 pre-signed URL generation + validation
│   └── schemas/
│       ├── auth_schema.py
│       ├── user_schema.py
│       ├── post_schema.py
│       ├── interaction_schema.py
│       ├── upload_schema.py
│       └── common.py               # Unified API response wrapper
├── tests/
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Setup Instructions

### 1. Clone & Install

```bash
git clone <repo-url>
cd joytapp-backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your MongoDB URI, JWT secrets, and AWS credentials
```

Generate strong JWT secrets:
```bash
python -c "import secrets; print(secrets.token_hex(64))"
```

### 3. Run with Docker (Recommended)

```bash
docker-compose up --build
```

This starts the API on `http://localhost:8000` and MongoDB on port `27017`.

### 4. Run Locally (without Docker)

Ensure MongoDB is running, then:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

---

## API Reference

### Auth

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | ❌ | Register new user |
| POST | `/api/v1/auth/login` | ❌ | Login, receive tokens |
| POST | `/api/v1/auth/refresh-token` | ❌ | Rotate refresh token |
| POST | `/api/v1/auth/logout` | ❌ | Revoke refresh token |

### Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/users/profile` | ✅ | Get own profile |
| PUT | `/api/v1/users/profile` | ✅ | Update own profile |
| PUT | `/api/v1/users/profile/image` | ✅ | Set profile image URL post-upload |
| GET | `/api/v1/users/{user_id}` | ❌ | Get public profile |

### Posts

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/posts` | ✅ | Create post |
| GET | `/api/v1/posts` | ❌ | List posts (paginated, filterable) |
| GET | `/api/v1/posts/{id}` | ❌ | Get single post |
| PUT | `/api/v1/posts/{id}` | ✅ | Update post (owner only) |
| DELETE | `/api/v1/posts/{id}` | ✅ | Soft-delete post (owner only) |

**Query params for GET /posts:** `page`, `page_size`, `title` (regex search), `date_from`, `date_to`

### Interactions

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/posts/{id}/like` | ✅ | Toggle like (like/unlike) |
| POST | `/api/v1/posts/{id}/comment` | ✅ | Add comment |
| GET | `/api/v1/posts/{id}/comments` | ❌ | List comments (paginated) |

### Uploads

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/uploads/presigned-url` | ✅ | Generate S3 pre-signed PUT URL |

---

## File Upload Flow

```
Client → POST /uploads/presigned-url
       ← { upload_url, file_url, key, expires_in }

Client → PUT <upload_url>  (direct to S3, with Content-Type header)
       ← 200 OK from S3

Client → PUT /users/profile/image  { image_url: file_url }
       ← updated profile
```

---

## Authentication Flow

```
POST /auth/register  →  { access_token, refresh_token }
POST /auth/login     →  { access_token, refresh_token }

# Use access_token in all protected requests:
Authorization: Bearer <access_token>

# When access_token expires (30 min default):
POST /auth/refresh-token  { refresh_token }  →  { new access_token, new refresh_token }

# Logout:
POST /auth/logout  { refresh_token }  →  token revoked in DB
```

---

## Design Decisions

- **Modular Monolith**: Each concern (auth, users, posts, interactions, uploads) is a self-contained vertical slice with its own endpoint, service, and repository layer.
- **Repository Pattern**: All MongoDB queries are isolated in repository classes. Services never touch the DB directly — keeping business logic clean and testable.
- **Soft Deletes**: Posts are never hard-deleted. `is_deleted: true` is set and all queries filter by `is_deleted: {$ne: true}`. Enables audit trails and recovery.
- **Duplicate Like Prevention**: A compound unique MongoDB index on `(post_id, user_id)` in the `likes` collection guarantees idempotency at the DB level. The toggle logic then handles like/unlike gracefully.
- **Refresh Token Rotation**: Every refresh issues a new pair of tokens and revokes the old refresh token. Supports revocation on logout. TTL index auto-purges expired tokens.
- **Presigned URLs**: Files never pass through the API server — clients upload directly to S3. The API only validates type/size and issues a time-limited signed URL.
- **Pagination**: Consistent `page` / `page_size` / `total` / `total_pages` envelope on all list endpoints.
- **Config-Driven**: All environment-specific values in `.env` via `pydantic-settings`. Zero hardcoded secrets.

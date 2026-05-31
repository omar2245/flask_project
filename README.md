# FastAPI Social API

A backend API for a simple social networking service, rebuilt from a Flask project into FastAPI.

The project includes user authentication, JWT access/refresh tokens, user profiles, follow relationships, posts, comments, and like features. It uses PostgreSQL as the database and SQLAlchemy as the ORM.

## Features

- User registration and login
- Password hashing with bcrypt
- JWT access token and refresh token authentication
- Current user profile query and update
- Public user profile query
- Follow, unfollow, follower list, following list, and follow statistics
- Post CRUD
- Comment CRUD
- Post likes and comment likes
- Pagination for list APIs
- FastAPI automatic Swagger documentation
- PostgreSQL database integration
- Docker, Gunicorn, Uvicorn worker, and Render deployment config

## Tech Stack

| Area | Technology |
| --- | --- |
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Authentication | JWT |
| Password Hashing | bcrypt |
| Deployment | Docker, Gunicorn, Uvicorn, Render |
| Config | python-dotenv, environment variables |

## Project Structure

```text
fastapi_app/
|-- main.py                  # FastAPI application entry point
|-- dependencies.py          # Shared dependencies, such as JWT user parsing
|-- api/
|   `-- v1/
|       |-- router.py         # API router registration
|       `-- endpoints/        # Route handlers
|-- core/                    # Security and config helpers
|-- db/                      # Database session setup
|-- models/                  # SQLAlchemy models
|-- schemas/                 # Pydantic request and response schemas
`-- services/                # Business logic and database operations
```

The old Flask files are still kept in the repository for migration history, but the current deployment entry point is:

```text
fastapi_app.main:app
```

## API Overview

### Auth

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/login` | Login and receive access/refresh tokens |
| POST | `/api/v1/auth/refresh` | Use refresh token to get a new access token |

### Users

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/v1/users/me` | Get current user profile |
| PUT | `/api/v1/users/me` | Update current user profile |
| GET | `/api/v1/users/{user_id}` | Get public user profile |
| GET | `/api/v1/users/{user_id}/posts` | Get posts created by a user |
| POST | `/api/v1/users/{user_id}/follow` | Follow a user |
| DELETE | `/api/v1/users/{user_id}/follow` | Unfollow a user |
| GET | `/api/v1/users/{user_id}/followers` | Get follower list |
| GET | `/api/v1/users/{user_id}/following` | Get following list |
| GET | `/api/v1/users/{user_id}/follow-stats` | Get follower/following counts |
| GET | `/api/v1/users/{user_id}/is-following` | Check whether current user follows target user |

### Posts

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/v1/posts` | Create a post |
| GET | `/api/v1/posts` | Get post list |
| GET | `/api/v1/posts/{post_id}` | Get post detail |
| PUT | `/api/v1/posts/{post_id}` | Update own post |
| DELETE | `/api/v1/posts/{post_id}` | Delete own post |
| GET | `/api/v1/posts/{post_id}/comments` | Get comments for a post |
| POST | `/api/v1/posts/{post_id}/like` | Like a post |
| DELETE | `/api/v1/posts/{post_id}/like` | Unlike a post |
| DELETE | `/api/v1/posts/{post_id}/unlike` | Compatibility alias for unlike |
| GET | `/api/v1/posts/{post_id}/like` | Get users who liked a post |

### Comments

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/v1/comments` | Create a comment |
| PUT | `/api/v1/comments/{comment_id}` | Update own comment |
| DELETE | `/api/v1/comments/{comment_id}` | Delete own comment |
| POST | `/api/v1/comments/{comment_id}/like` | Like a comment |
| DELETE | `/api/v1/comments/{comment_id}/like` | Unlike a comment |
| DELETE | `/api/v1/comments/{comment_id}/unlike` | Compatibility alias for unlike |
| GET | `/api/v1/comments/{comment_id}/like` | Get users who liked a comment |

## Authentication

Protected APIs require an access token in the request header:

```http
Authorization: Bearer <access_token>
```

The refresh API uses a refresh token in the same header format.

## Environment Variables

Create a `.env` file or configure these variables in the deployment environment:

```env
DATABASE_URL=postgresql://user:password@host:5432/database
JWT_SECRET_KEY=your_jwt_secret
PORT=8080
```

Depending on your local configuration, the database URL may also be named `SQLALCHEMY_DATABASE_URI`.

## Local Development

### 1. Create and activate virtual environment

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the FastAPI server

```bash
python -m uvicorn fastapi_app.main:app --reload
```

Default local URL:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Docker

```bash
docker build -t fastapi-social-api .
docker run --env-file .env -p 8080:8080 fastapi-social-api
```

The Dockerfile starts the app with Gunicorn and Uvicorn worker:

```bash
gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 -k uvicorn.workers.UvicornWorker fastapi_app.main:app
```

## Render Deployment

`render.yaml` is configured to run the FastAPI app:

```yaml
buildCommand: pip install -r requirements.txt
startCommand: gunicorn -k uvicorn.workers.UvicornWorker fastapi_app.main:app --bind 0.0.0.0:$PORT
```

## Example Requests

### Register

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"demo_user\",\"email\":\"demo@example.com\",\"password\":\"password123\"}"
```

### Login

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"account\":\"demo_user\",\"password\":\"password123\"}"
```

### Create Post

```bash
curl -X POST http://127.0.0.1:8000/api/v1/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d "{\"content\":\"Hello FastAPI\",\"images\":[]}"
```

## What I Practiced in This Project

- Migrating a Flask API structure to FastAPI
- Designing layered backend structure with routers, schemas, services, models, and dependencies
- Using Pydantic for request and response validation
- Using FastAPI dependency injection for database sessions and JWT authentication
- Building RESTful APIs with pagination and permission checks
- Mapping existing PostgreSQL tables with SQLAlchemy models
- Preparing the project for deployment with Docker and Render

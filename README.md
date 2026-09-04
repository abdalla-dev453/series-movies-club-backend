# ReelClub — Backend

Flask API for the TV Series & Movies Club app. Monolithic Flask + SQLAlchemy
backend, JWT auth, one blueprint per resource.

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # then fill in real secrets
flask db init                     # first time only
flask db migrate -m "initial schema"
flask db upgrade

flask run                         # or: python run.py
```

Run tests:

```bash
pytest
```

## Environment variables

| Variable | Purpose |
|---|---|
| `FLASK_ENV` | `development` \| `testing` \| `production` — selects the config class in `config.py` |
| `SECRET_KEY` | Flask session/signing secret |
| `JWT_SECRET_KEY` | Signing secret for access/refresh tokens |
| `DATABASE_URL` | SQLAlchemy DB URI (Postgres in prod, SQLite by default in dev) |
| `CORS_ORIGINS` | Comma-separated frontend origins allowed to call the API |

For a deployed frontend, set `CORS_ORIGINS` to its exact URL (for example,
`https://your-frontend.vercel.app`) and set the frontend's `VITE_API_URL` to
the deployed backend URL before building.

## Auth model

Short-lived access tokens (30 min) + refresh tokens (30 days), via
flask-jwt-extended. `POST /logout` adds the current token's `jti` to a
`token_blocklist` table, checked on every request — this is what makes
logout actually work with otherwise-stateless JWTs.

## Known limitations (MVP scope cuts)

- **No platform-level admin/moderator role.** Every permission check is
  club-scoped (`club_members.role == 'admin'`). There is no user who can
  moderate across clubs. Documented here as a deliberate cut, not an
  oversight — add a `users.is_platform_admin` flag (or a separate roles
  table) if that's needed later.
- **`clubs.created_by` is display-only.** It's shown as "founded by" but
  never used for permission checks — those always go through
  `club_members.role`. A club survives its creator's account being deleted.

## Folder layout

```
app/
├── __init__.py     # app factory (create_app)
├── extensions.py   # db, migrate, jwt, cors instances
├── models/         # one file per table
├── routes/         # one blueprint per resource — HTTP concerns only
├── schemas/        # request validation + response serialization
└── utils/          # decorators, permission checks, pagination, error handlers
```
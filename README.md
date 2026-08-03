# NudgeFlow - Intelligent Communication Timing Engine

NudgeFlow is an event-driven decision service that recommends the best **time** and **channel** for the next customer communication. It learns from a person's previous nudges and delivery outcomes, then produces an explainable recommendation for a newly received event such as a payment due date, cart abandonment, renewal, signup, or support follow-up.

It is designed as an assignment-quality implementation of the core workflow behind a provider-agnostic engagement platform:

1. An upstream system sends a customer event.
2. The engine evaluates recent nudge and delivery history for that customer.
3. It recommends when and how to nudge them next.
4. Delivery reports update the customer's engagement profile for future decisions.

The repository contains a FastAPI service, PostgreSQL schema and migrations, a Next.js dashboard, API documentation, Docker configuration, sample data, and automated tests.

## Product capabilities

- Ingest customer events with a type, timestamp, and business priority.
- Record outbound nudges across WhatsApp, email, SMS, and push.
- Accept delivery reports such as delivered, opened, clicked, replied, and failed.
- Prevent late provider reports from downgrading stronger engagement already observed.
- Recommend a personalized send time and channel from the previous 30 days of behavior.
- Return an event-specific safe fallback schedule when no history exists.
- Explain why the recommendation was made and expose a confidence score.
- Visualize engagement by time window and channel in a responsive dashboard.
- Switch the dashboard between Deep Zinc dark mode and Warm Slate light mode.

> The project is a decisioning engine. It does not send a WhatsApp, SMS, email, or push notification itself. A production delivery worker/provider integration would consume the returned recommendation and create the actual message.

## Demo flow

```text
Customer event
     |
     v
POST /api/events
     |
     v
GET /api/events/{event_id}/recommendation
     |
     v
Recommended time + channel + confidence + reason
     |
     v
Send through a communication provider (outside this service)
     |
     v
POST /api/delivery-reports
     |
     +--> Future recommendations improve from the new outcome
```

## Technology stack

| Area | Technology |
| --- | --- |
| API | Python, FastAPI, Pydantic v2 |
| Persistence | PostgreSQL 16, SQLAlchemy 2.0, Alembic |
| Local demo database | SQLite (optional, no Docker required) |
| Frontend | Next.js 15, React 18, TypeScript, Tailwind CSS |
| Runtime | Docker and Docker Compose |
| Tests | Pytest, FastAPI TestClient, in-memory SQLite |

## Repository layout

```text
.
├── backend/
│   ├── app/
│   │   ├── routers/          # HTTP endpoints
│   │   ├── services/         # Recommendation and analytics logic
│   │   ├── repositories/     # Database queries and updates
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic request/response contracts
│   │   └── utils/            # Time buckets and scoring helpers
│   ├── alembic/              # PostgreSQL migrations
│   ├── tests/                # Automated API and behavior tests
│   └── seed.py               # Demo-data generator
├── frontend/
│   ├── app/                  # Next.js App Router and global theme styles
│   ├── components/           # Forms, recommendation card, analytics
│   └── lib/api.ts            # Typed API client
├── docker-compose.yml
└── .env.example
```

## How recommendations work

### Time windows

Historical nudges are grouped by the hour at which they were sent:

| Window | Hours |
| --- | --- |
| 6 AM - 9 AM | 06:00 - 08:59 |
| 9 AM - 12 PM | 09:00 - 11:59 |
| 12 PM - 3 PM | 12:00 - 14:59 |
| 3 PM - 6 PM | 15:00 - 17:59 |
| 6 PM - 9 PM | 18:00 - 20:59 |
| 9 PM - 12 AM | 21:00 - 23:59 |

An overnight bucket is retained for analytics, but it is never selected as a recommended sending window.

### Engagement scoring

Each nudge receives a value according to its latest known outcome:

| Delivery status | Score |
| --- | ---: |
| `REPLIED` | 5 |
| `CLICKED` | 3 |
| `OPENED` | 2 |
| `DELIVERED` | 1 |
| `FAILED` | -3 |

More recent evidence matters more:

```text
recency_weight = 1 / (days_old + 1)
weighted_score = engagement_score * recency_weight
```

For the selected lookback period (30 days by default), the service sums weighted scores by time window and channel. It selects the strongest non-overnight time window and the strongest channel with positive engagement. Confidence is the winning time-window score divided by the total absolute score across windows.

### Delivery-report behavior

Delivery reports are validated against the supported status values. Status updates are monotonic:

```text
FAILED < DELIVERED < OPENED < CLICKED < REPLIED
```

For example, if a `REPLIED` report was recorded and a delayed `DELIVERED` webhook arrives afterwards, the nudge remains `REPLIED`. This keeps out-of-order provider webhooks from corrupting the learning signal.

### New customers and events

An event-specific recommendation always returns a decision. If the person has no recent history, the engine returns:

- Channel: `WHATSAPP`
- Confidence: `0.0`
- Timing: five minutes from now during a safe daytime/evening window, or 9:00 AM if the event is received overnight
- Reason: a clear explanation that the result is a fallback rather than a learned preference

When an event timestamp is in the future, the recommendation is never scheduled before that event.

## API reference

Interactive API documentation is available at `http://localhost:8000/docs` while the backend is running.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Liveness check |
| `POST` | `/api/events` | Create a customer event |
| `GET` | `/api/events` | List events; filter with `user_id` |
| `GET` | `/api/events/{event_id}` | Retrieve an event |
| `GET` | `/api/events/{event_id}/recommendation` | Get the recommended next nudge for an event |
| `POST` | `/api/nudges` | Record an outbound nudge |
| `GET` | `/api/nudges` | List nudges; filter with `user_id` |
| `GET` | `/api/nudges/{nudge_id}` | Retrieve a nudge |
| `POST` | `/api/delivery-reports` | Record an outcome from a provider/webhook |
| `GET` | `/api/recommendation/{user_id}` | Get a user-level recommendation from history |
| `GET` | `/api/users/{user_id}/analytics` | Get engagement breakdown and recommendation |

`GET /api/recommendation/{user_id}` supports optional query parameters:

- `lookback_days`: integer from `1` to `365`; defaults to `30`.
- `event_id`: optional event identifier. It must belong to the same user and ensures timing is not before the event.

### Example requests

Create an event:

```bash
curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "customer_42",
    "event_type": "payment_due",
    "event_time": "2026-08-03T10:00:00Z",
    "priority": "HIGH"
  }'
```

Record a sent nudge:

```bash
curl -X POST http://localhost:8000/api/nudges \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "customer_42",
    "channel": "WHATSAPP",
    "sent_time": "2026-08-02T19:00:00Z",
    "status": "DELIVERED"
  }'
```

Submit a provider report:

```bash
curl -X POST http://localhost:8000/api/delivery-reports \
  -H "Content-Type: application/json" \
  -d '{
    "nudge_id": "<nudge-uuid>",
    "status": "REPLIED",
    "meta": "provider_message_id_123"
  }'
```

Get the event decision:

```bash
curl http://localhost:8000/api/events/<event-uuid>/recommendation
```

Example response:

```json
{
  "user_id": "customer_42",
  "event_id": "b1ffb97a-4afd-4e91-8943-6c91b495d032",
  "recommended_time": "2026-08-03T19:00:00+00:00",
  "channel": "WHATSAPP",
  "confidence": 0.91,
  "reason": "User has replied to 4 Whatsapp nudges between 6 PM - 9 PM during the last 30 days."
}
```

## Run with Docker (recommended for PostgreSQL)

### Prerequisites

- Docker Desktop with Docker Compose

### Start the stack

```bash
cp .env.example .env
docker compose up --build
```

On Windows PowerShell, use:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Services:

| Service | Address |
| --- | --- |
| Dashboard | http://localhost:3000 |
| FastAPI / Swagger | http://localhost:8000 / http://localhost:8000/docs |
| PostgreSQL | `localhost:5432` |

Migrations run automatically when the backend container starts. To populate demo data:

```bash
docker compose exec backend python seed.py
```

> `seed.py` deletes existing events and nudges before adding demonstration data. Use it only in a disposable development environment.

## Run locally without Docker (SQLite demo mode)

This option is useful when Docker Desktop is not installed. SQLite is suitable for a local demo and test data only; use PostgreSQL for a shared or production deployment.

### Prerequisites

- Python 3.12+ with the backend dependencies installed
- Node.js 20+ and npm

### Terminal 1 - backend

```powershell
cd backend
$env:DATABASE_URL = "sqlite:///./ict_engine.db"
python -c "from app.database import Base, engine; import app.models; Base.metadata.create_all(bind=engine)"
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2 - frontend

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open `http://localhost:3000`. Keep both terminals running while using the application.

### PostgreSQL local development

For a local PostgreSQL instance, set `DATABASE_URL` in `backend/.env`, then run:

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Dashboard guide

The dashboard is both a product demo and a manual test surface.

1. **Create Event**: add the business trigger for a user. A scheduling decision is shown immediately.
2. **Create Nudge**: record historical or newly sent communications.
3. **Submit Delivery Report**: update the result of a nudge with data from a provider.
4. **Recommendation**: retrieve the best learned time and channel for any user.
5. **Analytics**: inspect score distribution by time window and channel.
6. **Theme toggle**: use the control in the top-right navigation to switch between dark and light themes.

For the strongest personalized demo, create several WhatsApp nudges for the same user at around 7 PM, submit `REPLIED` delivery reports, then create an event for that user. The recommended time should favor the evening WhatsApp window and the explanation should reflect the historical engagement.

## Testing and quality checks

Backend tests use an in-memory SQLite database and require no running PostgreSQL server:

```bash
cd backend
python -m pytest -v
```

The suite includes event CRUD, recommendation behavior, analytics, delivery-report updates, invalid status validation, event fallback scheduling, and out-of-order report protection.

Validate the frontend TypeScript project:

```bash
cd frontend
npm.cmd exec tsc -- --noEmit
```

Create an optimized frontend build:

```bash
cd frontend
npm.cmd run build
```

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | PostgreSQL Docker connection | SQLAlchemy connection string |
| `APP_ENV` | `development` | Application environment label |
| `POSTGRES_USER` | `ict_user` | Docker PostgreSQL user |
| `POSTGRES_PASSWORD` | `ict_password` | Docker PostgreSQL password |
| `POSTGRES_DB` | `ict_engine` | Docker PostgreSQL database |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Backend base URL used by the frontend |

Never commit real credentials. Use a secret manager or managed platform configuration for production deployments.

## Production considerations

This repository establishes the core decisioning workflow. A production implementation should additionally include:

- Authentication, tenant isolation, authorization, and rate limiting.
- A user profile containing IANA timezone and consent/channel preferences.
- A queue and scheduler to persist and execute recommended sends.
- Provider adapters for WhatsApp, SMS, RCS, email, push, and voice.
- Signed webhook verification, idempotency keys, and retry policies.
- Delivery-report deduplication and a full provider event audit trail.
- Observability: structured logs, metrics, tracing, alerts, and dead-letter handling.
- Encryption, retention controls, PII minimization, and compliance workflows.
- More robust ranking features, experimentation, suppression rules, and send-frequency caps.

## License

This project is provided as an engineering assignment and demonstration implementation. Add the appropriate license before external distribution.


# QuickBooks Integration Project

This project integrates QuickBooks Online with a Python FastAPI backend and a React-based frontend UI. It supports OAuth2 authorization, token validation, account fetching with prefix search, and auto-backup of the PostgreSQL database.

##  Features

- OAuth2.0 flow with QuickBooks
- Account search by prefix
- Access token validation (server-side)
- PostgreSQL storage with auto-backup every hour
- Toggle between API-only mode (Postman) and full web UI mode
- Fully containerized with Docker Compose

---

##  Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- QuickBooks Developer account: https://developer.intuit.com/app/developer/homepage

---

##  How to Run

1. **Clone the repo**

```bash
git clone https://github.com/fanando/QuickBook_integration_project.git
cd quickbooks-integration
```

2. **Create a `.env` file in the root directory**

```env
CLIENT_ID=YOUR_CLIENT_ID
CLIENT_SECRET=YOUR_CLIENT_SECRET
REDIRECT_URI=http://localhost:8000/auth/callback
QBO_SANDBOX_BASE=https://sandbox-quickbooks.api.intuit.com
START_UP_PERIOD=5
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/qbo
USE_UI=True
```

> 💡 You get your `CLIENT_ID` and `CLIENT_SECRET` from [QuickBooks Developer Console](https://developer.intuit.com/app/developer/homepage) by registering a new app.

3. **Run the app**

```bash
docker-compose up --build
```

> The first build may take a couple of minutes.

---

## 🌐 Accessing the App

| Mode      | USE_UI | Access via                     |
|-----------|--------|--------------------------------|
| UI Mode   | 1     | `http://localhost:3000`        |
| API Mode  | 0     | Use Postman on port `8000`     |

> When `USE_UI=1`, the app launches a React interface.  
> When `USE_UI=0`, you can test endpoints using Postman or cURL.

---

## OAuth2 Flow

1. Visit `http://localhost:3000` (if `USE_UI=True`) and click "Connect to QuickBooks".
2. Log in and authorize your app.
3. The token is securely saved and used for subsequent API calls.

Alternatively, in API-only mode, initiate auth from:
Using browser or postman
```http
GET http://localhost:8000/auth/authorize
```

Tokens are validated on every `/accounts` request.

---

##  API Endpoints

- `GET /auth/authorize`: Starts the OAuth2 flow
- `GET /auth/callback`: Handles QuickBooks callback
- `GET /accounts?prefix=...`: Returns matching accounts (requires Bearer token)

---

##  Database

- PostgreSQL runs in a Docker container.
- Auto-backups are saved every hour to `./pg_backups`.

---

##  Folder Structure

```
.
├── api-service/        # FastAPI backend
├── crawler-service/    # Scheduled QuickBooks crawler
├── ui/                 # React + Vite frontend (optional)
├── pg_backups/         # Hourly DB backups
├── .env                # Environment config
└── docker-compose.yml  # Orchestrates all services
```

---

##  Tips for Devs

- Add `localhost:3000/auth/callback` and `localhost:8000/auth/callback` as **redirect URIs** in the QuickBooks app settings.
- If you want to start fresh:  
  ```bash
  docker-compose down -v
  ```

---


## 📄 License

MIT License

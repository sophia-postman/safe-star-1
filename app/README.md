# SafeStar Service API — Python Implementation

A Flask-based implementation of the **SafeStar Service API**, which tracks driver and vehicle safety metrics and generates personalized Driver Messages.

---

## Project Structure

```
app/
├── main.py               # App entry point & blueprint registration
├── auth.py               # JWT Bearer authentication decorator
├── store.py              # In-memory data store
├── routes/
│   ├── driver.py         # Driver Safety Profile endpoints
│   ├── vehicle.py        # Vehicle Safety Profile endpoints
│   ├── run.py            # Safety Scan Run endpoints
│   ├── display.py        # Driver Message Display endpoint
│   └── diagnostics.py    # Diagnostic Reporting endpoints
requirements.txt          # Python dependencies
```

---

## Prerequisites

- Python 3.9+
- pip

---

## Installation

```bash
# 1. Clone the repo and navigate to the project root
cd safe-star-1

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Configuration

The app reads the following environment variables (all optional — defaults shown):

| Variable     | Default            | Description                        |
|--------------|--------------------|------------------------------------|
| `JWT_SECRET` | `safestar-secret`  | Secret used to sign/verify JWTs    |
| `PORT`       | `5000`             | Port the server listens on         |
| `FLASK_ENV`  | `development`      | Flask environment mode             |

You can set them in a `.env` file at the project root:

```env
JWT_SECRET=your-super-secret-key
PORT=5000
```

---

## Running the Server

```bash
python app/main.py
```

The API will be available at `http://localhost:5000`.

---

## Authentication

All endpoints require a **JWT Bearer token** in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

### Generate a test token

```python
import jwt
token = jwt.encode({"sub": "test-user"}, "safestar-secret", algorithm="HS256")
print(token)
```

Or use the Postman collection — set the `jwtSecret` variable to `safestar-secret` and the collection will generate the token automatically.

---

## API Endpoints

### Driver Safety

| Method   | Path              | Description                    |
|----------|-------------------|--------------------------------|
| `POST`   | `/driver/:id`     | Create Driver Safety Profile   |
| `GET`    | `/driver/:id`     | Retrieve Driver Safety Profile |
| `PUT`    | `/driver/:id`     | Update Driver Safety Profile   |
| `DELETE` | `/driver/:id`     | Delete Driver Safety Profile   |

### Vehicle Safety

| Method   | Path              | Description                     |
|----------|-------------------|---------------------------------|
| `POST`   | `/vehicle/:id`    | Create Vehicle Safety Profile   |
| `GET`    | `/vehicle/:id`    | Retrieve Vehicle Safety Profile |
| `PATCH`  | `/vehicle/:id`    | Update Vehicle Safety Profile   |
| `DELETE` | `/vehicle/:id`    | Delete Vehicle Safety Profile   |

### Safety Scan

| Method   | Path         | Description          |
|----------|--------------|----------------------|
| `POST`   | `/run`       | Start a safety scan  |
| `GET`    | `/run/:id`   | Get run status       |
| `DELETE` | `/run/:id`   | Cancel a run         |

### Display

| Method | Path       | Description                              |
|--------|------------|------------------------------------------|
| `GET`  | `/display` | Get personalized Driver Message display  |

### Diagnostics

| Method | Path                           | Description                    |
|--------|--------------------------------|--------------------------------|
| `POST` | `/diagnostics/generate/:vehicleId` | Generate diagnostic report |
| `GET`  | `/diagnostics/:id`             | Retrieve diagnostic report     |
| `POST` | `/diagnostics/send/:id`        | Send diagnostic report         |

---

## Using with Postman

1. Open the **SafeStar Service** workspace in Postman.
2. Select the **Local** environment.
3. Set `baseUrl` to `http://localhost:5000`.
4. Set `jwtSecret` to match your `JWT_SECRET` env var (default: `safestar-secret`).
5. Run requests from the **SafeStar Service API** collection.

---

## Notes

- **Storage is in-memory only** — all data is lost when the server restarts. This is intentional for local development and testing.
- The `/display` endpoint reads from existing driver and vehicle profiles in the store to generate a personalized message.
- The `/run` endpoint advances status from `QUEUED` → `COMPLETE` on the first `GET` call.

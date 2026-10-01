# ResQNet

ResQNet is a role-based emergency reporting and response coordination application. Citizens can report fire, medical, and accident emergencies. The FastAPI backend geocodes locations, calculates a priority score, stores the incident in MySQL, and exposes authenticated API endpoints. Operators can review active incidents, compare compatible available resources by distance, dispatch a unit, and complete tasks. Administrators can add and release ambulances and fire trucks.

The user interface is a Streamlit application and the backend is a FastAPI application. Geoapify is optional: it provides address geocoding, driving routes, and a static map when an API key is configured. Coordinate input and a local distance fallback keep the application usable for local testing without Geoapify.

## Features

- Citizen registration, login, emergency reporting, status tracking, and completion of assigned emergencies
- Emergency types: `fire`, `medical`, and `accident`
- Severity levels: `low`, `medium`, `high`, and `critical`
- Priority scoring from severity and number of people affected, with an optional scikit-learn model
- Operator dashboard with active incidents sorted by priority and dispatch history
- Resource matching by emergency type and distance
  - `fire` emergencies require a `fire_truck`
  - `medical` and `accident` emergencies require an `ambulance`
- Admin resource management for adding and releasing units
- Geoapify static map when configured, otherwise a Streamlit map using stored coordinates
- MySQL trigger that changes an emergency to `assigned` and a resource to `dispatched` after dispatch

## Tech stack

| Layer | Technology |
| --- | --- |
| API | FastAPI and Uvicorn |
| Database | MySQL with raw SQL through PyMySQL |
| Frontend | Streamlit |
| Authentication | JWT with `python-jose`; password hashing with Passlib/bcrypt |
| Maps and geocoding | Geoapify, with coordinate and Haversine fallbacks |
| Optional machine learning | pandas, scikit-learn, and joblib |

## Project structure

```text
ResQNet/
├── backend/
│   ├── main.py                 # FastAPI application and /health endpoint
│   ├── config.py               # Environment-backed configuration
│   ├── database.py             # MySQL connection handling
│   ├── dependencies.py         # Database and JWT dependencies
│   ├── schemas.py              # Pydantic request and response models
│   ├── routes/                 # Authentication, emergency, and resource endpoints
│   ├── queries/                # Raw SQL query functions
│   ├── services/               # Authentication, maps, allocation, and priority logic
│   ├── ml/                     # Training data, training scripts, and model artifact
│   └── requirements.txt
├── database/
│   └── schema.sql              # Database, tables, view, and dispatch trigger
├── frontend_streamlit/
│   ├── app.py                  # Login, registration, and role-based navigation
│   ├── api_client.py           # HTTP client for the FastAPI backend
│   ├── pages/
│   │   ├── 1_Report_Emergency.py
│   │   ├── 2_Operator_Dashboard.py
│   │   └── 3_Admin_Panel.py
│   └── requirements.txt
├── tests/
│   └── test_priority.py
└── README.md
```

## Requirements

- Python 3.10 or newer
- MySQL Server running locally or in Docker/XAMPP
- PowerShell on Windows, or an equivalent shell on another platform
- Optional: a Geoapify API key for address lookup, driving routes, and static maps

## Run locally

Run these commands from the repository root.

### 1. Create a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
pip install -r frontend_streamlit\requirements.txt
```

### 2. Create the database

Start MySQL and apply the schema:

```powershell
mysql -u root -p < database\schema.sql
```

The schema creates the `emergency_db` database and the `users`, `resources`, `emergencies`, and `dispatches` tables. It also creates the `active_emergencies` view and the dispatch trigger.

### 3. Configure the backend

Create `backend/.env` with values appropriate for your MySQL installation:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=emergency_db
JWT_SECRET=replace_with_a_long_random_secret
GEOAPIFY_API_KEY=your_geoapify_key
```

`GEOAPIFY_API_KEY` may be left empty for local coordinate-based testing. With no key, enter locations as `latitude,longitude`; dispatch distance uses a Haversine estimate multiplied by `1.25` instead of a Geoapify driving route. The default JWT secret is for development only and should be replaced.

### 4. Start the API

In one terminal, from the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --port 8000
```

Check `http://localhost:8000/health` and open `http://localhost:8000/docs` for the interactive API documentation.

### 5. Start Streamlit

The frontend client defaults to `http://localhost:8001`, so set it to the API port used above before starting Streamlit:

```powershell
$env:RESQNET_API_URL = "http://localhost:8000"
.\.venv\Scripts\Activate.ps1
streamlit run frontend_streamlit\app.py
```

Open `http://localhost:8501`. The sidebar pages are selected from the authenticated user role:

| Role | Available UI | Main actions |
| --- | --- | --- |
| Citizen | Report emergency | Create reports, view history, complete assigned reports |
| Operator | Operator dashboard | View active incidents, inspect compatible units, dispatch, complete tasks |
| Admin | Admin panel | Add resources, view resources, release dispatched resources |

New registrations are always created as `citizen` accounts. Operator and admin accounts must be assigned directly in the database for development or provisioned by an administrative process that is not included in this repository. For example, after registering an account, update its role in MySQL:

```sql
USE emergency_db;
UPDATE users SET role = 'operator' WHERE email = 'operator@example.com';
UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';
```

## Application flow

1. A citizen creates an account and signs in.
2. The citizen submits an emergency type, severity, number of people affected, and either an address or GPS coordinates.
3. The API resolves the location, calculates a priority score from 0 to 100, and stores the report with status `reported`.
4. An operator sees active reports ordered by priority and can inspect available compatible resources.
5. The allocation service filters resources by type and ranks the remaining units by distance. Geoapify driving distance is used when available; otherwise the local fallback is used.
6. Dispatching creates one dispatch record. The MySQL trigger changes the emergency to `assigned` and the resource to `dispatched`.
7. The citizen, operator, or admin can complete an assigned emergency. The API marks it `resolved` and makes its resource available again.

## API overview

All endpoints below except registration, login, and health require `Authorization: Bearer <token>`.

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| GET | `/health` | Public | API and priority-model status |
| POST | `/register` | Public | Create a citizen account |
| POST | `/login` | Public | Return a JWT and role |
| POST | `/emergencies` | Citizen | Report an emergency |
| GET | `/emergencies` | Authenticated | List emergencies; citizens see their own reports |
| PATCH | `/emergencies/{emergency_id}/resolve` | Citizen, operator, admin | Complete an assigned emergency |
| GET | `/resources` | Operator, admin | List resources, optionally with `available_only=true` |
| POST | `/resources` | Admin | Add an ambulance or fire truck |
| GET | `/resources/for-emergency/{emergency_id}` | Operator | Rank compatible available resources |
| PATCH | `/resources/{resource_id}/release` | Admin | Release a resource and complete its task |
| POST | `/emergencies/{emergency_id}/dispatch` | Operator | Dispatch a selected or best-ranked resource |
| GET | `/dispatches` | Operator | View dispatch history |
| GET | `/map-url` | Operator | Return a Geoapify static map URL when configured |

## Optional priority model

The default priority calculation is deterministic:

- Severity points are `20` for low, `50` for medium, `75` for high, and `100` for critical.
- The people-affected bonus is two points per person, capped at 30.
- The final formula score is capped at 100.

The optional model uses `severity_points` and `people_affected` to predict `priority_score`. Training data belongs in `backend/ml/training_data.csv` and must contain these numeric columns:

```csv
severity_points,people_affected,priority_score
20,1,22
50,5,60
100,15,100
```

Generate sample data and train the model from the repository root:

```powershell
python -m backend.ml.generate_simulation_data
python -m backend.ml.train_model
```

Enable the trained artifact in `backend/.env` and restart the API:

```env
USE_ML_PRIORITY=true
MODEL_PATH=backend/ml/priority_model.joblib
```

The `/health` response reports whether the artifact exists and whether formula or ML scoring is active. Do not place names, addresses, passwords, or other personally identifying information in training data.

## Tests

The current automated test coverage includes the priority calculation:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest
```

The API and Streamlit workflows require a running MySQL instance and are currently best verified through the local application and FastAPI Swagger UI.

## Current limitations

- There is no built-in workflow for creating operator or admin accounts.
- Dispatch ranking uses distance after compatibility filtering; it does not combine distance with priority weighting.
- The fallback map is a coordinate map rather than an interactive route map.
- Notifications and hospital bed availability are not implemented.
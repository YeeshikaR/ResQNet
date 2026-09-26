### ResQNet

A web-based system that lets citizens report emergencies, automatically scores how urgent each one is, shows live incidents and available resources (ambulances/fire trucks) on a map, and intelligently dispatches the best available unit based on availability, proximity, and severity.

Built with **Python, FastAPI, MySQL (raw SQL), Streamlit, and Geoapify**.

---

##  Features

- **Emergency Reporting** — citizens submit incidents with type, severity, people affected, and location (address auto-converted to coordinates)
- **Priority Scoring** — every emergency gets an urgency score (0–100) based on severity and people affected
- **Live Map** — emergencies and available resources plotted on a map image, powered by Geoapify
- **Smart Dispatch** — automatically picks the best available resource using real road distance + priority weighting
- **Role-Based Access** — citizen, operator, and admin roles with separate dashboards
- **Auto-Updating Database** — a MySQL trigger keeps resource/emergency statuses in sync the moment a dispatch happens
- **(Optional) ML Priority Model** — a trained scikit-learn model as an upgrade to the base formula

---

##  Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| Database | MySQL (raw SQL via `pymysql`, no ORM) |
| Frontend | Streamlit |
| Maps / Location | Geoapify (Geocoding, Routing, Static Maps APIs) |
| Machine Learning (optional) | scikit-learn |
| Authentication | JWT (`python-jose`) + `passlib` for password hashing |

---

##  Project Structure

```
emergency-response-system/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── config.py
│   ├── schemas.py
│   ├── queries/          # raw SQL functions, grouped by table
│   ├── routes/           # API endpoints
│   ├── services/         # priority scoring, allocation logic, map calls
│   ├── ml/                # optional ML model training + artifacts
│   ├── requirements.txt
│   └── .env
├── frontend_streamlit/
│   ├── app.py
│   ├── api_client.py
│   ├── pages/
│   └── requirements.txt
├── database/
│   └── schema.sql
└── README.md
```

---

##  Setup Instructions

### 1. Prerequisites
- Python 3.10+
- MySQL Server (running locally, or via XAMPP/Docker)
- A free [Geoapify](https://www.geoapify.com/) API key (no credit card required)

### 2. Clone the repository
```bash
git clone <your-repo-url>
cd emergency-response-system
```

### 3. Set up the database
Open MySQL and run:
```bash
mysql -u root -p < database/schema.sql
```
This creates the `emergency_db` database with all tables, the `active_emergencies` view, and the auto-update trigger.

### 4. Configure environment variables
Create a `.env` file inside `backend/`:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=emergency_db
JWT_SECRET=some_random_secret_string
GEOAPIFY_API_KEY=your_geoapify_key
```

### 5. Install backend dependencies and run it
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
Backend runs at `http://localhost:8000` — visit `http://localhost:8000/docs` to test every endpoint directly.

### 6. Install frontend dependencies and run it
Open a new terminal:
```bash
cd frontend_streamlit
pip install -r requirements.txt
streamlit run app.py
```
Frontend runs at `http://localhost:8501`.

---

##  How It Works

1. A citizen submits an emergency report (type, severity, people affected, address) via Streamlit
2. The backend converts the address to coordinates using Geoapify's Geocoding API
3. A priority score is calculated from severity + people affected
4. The emergency is saved to MySQL
5. The operator dashboard displays all active emergencies on a map, sorted by priority
6. When an operator clicks **Dispatch**, the system filters available matching resources, checks real road distance via Geoapify's Routing API, and assigns the best-scoring one
7. A MySQL trigger automatically updates the resource's and emergency's status once the dispatch is recorded

##  Run Locally

The commands below are run from the repository root in two PowerShell terminals.

### 1. Create an environment and install dependencies

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
pip install -r frontend_streamlit\requirements.txt
```

### 2. Create the database and configuration

Start MySQL, then run:

```powershell
mysql -u root -p < database\schema.sql
Copy-Item backend\.env.example backend\.env
```

Edit `backend/.env` with your MySQL password. Add a Geoapify key for address lookup, road routing, and the static map. Without a key, enter a location as `latitude,longitude`; routing uses a local Haversine estimate and the rest of the application remains usable.

### 3. Start the API

```powershell
\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload
```

Test `http://localhost:8000/health` and use `http://localhost:8000/docs` for the interactive API.

### 4. Start Streamlit

In a second terminal:

```powershell
\.venv\Scripts\Activate.ps1
streamlit run frontend_streamlit\app.py
```

Open `http://localhost:8501`, create an account, and use the sidebar pages. Use an `admin` account to add ambulances and fire trucks. Operators can dispatch and resolve emergencies.

##  ML Training

The default priority calculation is deterministic and does not require a model. It uses severity points plus a capped people-affected bonus. The optional model learns the same two input features from a CSV and is loaded only when `USE_ML_PRIORITY=true`.

### Training data location and format

Put training data at `backend/ml/training_data.csv`. It must contain these numeric columns:

```csv
severity_points,people_affected,priority_score
20,1,22
50,5,60
100,15,100
```

`severity_points` should normally be `20` (low), `50` (medium), `75` (high), or `100` (critical). `priority_score` is the target value from 0 to 100. Replace the sample CSV with historical, reviewed incidents only; do not put passwords, names, addresses, or other personally identifying information into the training file.

### Generate, train, and enable the model

```powershell
python -m backend.ml.generate_simulation_data
python -m backend.ml.train_model
```

Training writes `backend/ml/priority_model.joblib`. This binary artifact is ignored by Git and is loaded by `priority_service.py`. To enable it, set this in `backend/.env`, then restart FastAPI:

```env
USE_ML_PRIORITY=true
MODEL_PATH=backend/ml/priority_model.joblib
```

The training command prints the test mean absolute error. Keep that metric with the dataset version when comparing models. Re-run training whenever the CSV changes. The API health endpoint reports whether the artifact exists and whether formula or ML scoring is active.

##  API Authentication Flow

1. `POST /register` with a name, email, and password. New accounts are always citizens.
2. `POST /login` to receive a JWT and role.
3. Send `Authorization: Bearer <token>` on protected requests.
4. Citizens can report emergencies and view only their own reports. Operators can view, dispatch, and resolve active emergencies. Admins can do operator actions and add resources; neither role can use the citizen reporting endpoint.

For a no-key smoke test, register a user, add resources using coordinates such as `40.7128,-74.0060`, report an emergency using the same coordinate format, and dispatch it from the operator dashboard.

---

##  API Overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/register` | Create a new user account |
| POST | `/login` | Authenticate and receive a JWT token |
| POST | `/emergencies` | Report a new emergency |
| GET | `/emergencies` | List emergencies (optionally filter by status) |
| GET | `/resources` | List resources (optionally filter by availability) |
| POST | `/resources` | Add a new resource (admin) |
| POST | `/emergencies/{id}/dispatch` | Dispatch the best available resource to an emergency |

Full interactive documentation is available at `/docs` once the backend is running.

---

##  Team

| Role | Responsibility |
|---|---|
| Database | Schema, raw SQL queries, authentication |
| Intelligence | Priority scoring (formula + optional ML model) |
| Allocation & Maps | Geoapify integration, dispatch decision logic |
| Frontend | Streamlit pages, API routing, end-to-end integration |

---

##  Future Improvements

- Interactive (clickable) map for setting emergency location
- Real-time notifications for operators
- Hospital bed-availability tracking and integration
- Historical analytics dashboard for response-time trends
- Deployment via Docker for easier setup

---


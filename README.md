# Travel API

A REST API for managing travel projects and places, built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy**. Places are sourced and validated via the **Art Institute of Chicago public API**.


---

## Docker Compose SetUp

```bash
# Clone / enter the project folder
cd src

# Copy and adjust env if needed
cp .env.example .env

# Start Postgres & FastAPI server
docker compose up --build

# API is now available at http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

---

## Running Locally (without Docker)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env

cd src

uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Postman Collection

Import `Travel_API.postman_collection.json` into Postman.  

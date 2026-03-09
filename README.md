# Fruit List – Full Stack Django Challenge

A full-stack application built entirely with **Django** (Python). Django serves both the REST API and the frontend HTML template.

---

## Project Structure

```
Test Project/
├── manage.py
├── requirements.txt
├── pytest.ini
├── fruitList.json
├── fruitproject/           ← Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── fruit/                  ← Django app
    ├── __init__.py
    ├── apps.py
    ├── views.py            ← API + page views
    ├── urls.py
    ├── templates/
    │   └── fruit/
    │       └── index.html  ← Frontend (vanilla JS)
    └── tests/
        ├── __init__.py
        └── test_views.py   ← 18 pytest tests
```

---

## How to Run

### Step 1 — Create and activate a virtual environment

```bash
cd "/Users/macbookpro/Downloads/Test Project"
python3 -m venv venv
source venv/bin/activate
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Run the Django development server

```bash
python manage.py runserver
```

Open your browser at **http://127.0.0.1:8000**

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Frontend HTML page |
| GET | `/fruit` | Return all fruit as JSON |
| GET | `/fruit?color=red` | Filter by color (case-insensitive) |
| GET | `/fruit?in_season=true` | Filter by in-season status |
| GET | `/fruit?name=app` | Partial case-insensitive name search |
| GET | `/fruit?color=red&in_season=true` | Combined filters |

---

## Run Tests

```bash
cd "/Users/macbookpro/Downloads/Test Project"
source venv/bin/activate
pytest -v
```

---

## Features

- Django serves the API **and** the frontend from the same server
- Filter by **color**, **in season**, and **name** (partial, case-insensitive)
- Filters sync with the **browser URL querystring**
- Back/forward browser navigation restores filters
- Fully styled responsive UI (pure HTML + CSS + vanilla JS — no Node required)
- 18 pytest tests covering all endpoints and filter combinations

# Fruit List – Full Stack Django Challenge

A full-stack fruit browsing application built entirely with **Python + Django**. A single Django server handles both the REST API and the HTML frontend — no Node.js, no npm, no separate frontend build step.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Approach Chosen & Why](#approach-chosen--why)
3. [Time Complexity](#time-complexity)
4. [Project Structure](#project-structure)
5. [How to Run](#how-to-run)
6. [API Endpoints](#api-endpoints)
7. [How to Run Tests](#how-to-run-tests)
8. [Edge Cases](#edge-cases)

---

## Architecture

```
Browser
  │
  │  GET /          → Django renders index.html (the full UI)
  │  GET /fruit     → Django returns filtered JSON array
  │
  ▼
Django Dev Server (port 8000)
  │
  ├── fruitproject/         ← Django project (settings, root URL config)
  └── fruit/                ← Django app
        ├── views.py        ← Two views: index (HTML) + fruit_api (JSON)
        ├── urls.py         ← Routes "" → index, "fruit" → fruit_api
        ├── templates/      ← index.html (jQuery AJAX frontend)
        └── tests/          ← 17 pytest-django tests

Static data source: fruitList.json (20 fruits, loaded once at startup)
```

The application follows a **Django monolith** pattern:

- **One server, two responsibilities** — Django's `render()` serves the HTML page; `JsonResponse` serves filtered JSON from the same process.
- **No database** — fruit data is static and lives in `fruitList.json`. It is read from disk exactly once when the server starts, then held in memory.
- **No frontend build pipeline** — the template is plain HTML + CSS. All interactivity is handled by jQuery (loaded from CDN) making AJAX calls back to the same Django server.

---

## Approach Chosen & Why

### Django over FastAPI / Flask
The assessment specified a fruit list that is filtered server-side. Django was chosen because it handles routing, template rendering, and JSON responses within a single unified framework, eliminating the need for a separate frontend server or build toolchain. The resulting project has fewer moving parts and is simpler to run.

### Static JSON file over a database
The fruit catalogue is fixed. Using a database would add migration overhead, a schema to maintain, and read queries on every request with no benefit. Loading `fruitList.json` at module level gives O(1) access time after startup.

### Module-level data loading (`FRUIT_LIST`)
```python
# fruit/views.py — executed once when Django imports the module
with open(BASE_DIR / "fruitList.json") as f:
    FRUIT_LIST = json.load(f)
```
Every API request works on a shallow copy of this list. There is **zero file I/O per request**.

### jQuery AJAX over native `fetch()`
jQuery's `$.ajax()` was chosen over the browser's built-in `fetch()` for three practical reasons:

| Concern | jQuery advantage |
|---------|-----------------|
| Aborting in-flight requests | `xhr.abort()` — trivial with jQuery's XHR object |
| Serialising query parameters | `$.param(obj)` — one call instead of `URLSearchParams` |
| Broader browser compatibility | jQuery normalises older browser quirks |

### In-memory SQLite for tests
Django's test runner requires a `DATABASES` configuration even when views do not touch the database. SQLite `:memory:` satisfies this requirement with no disk I/O and no migration side-effects.

---

## Time Complexity

### Data loading (startup — happens once)
| Operation | Complexity |
|-----------|-----------|
| Parse `fruitList.json` (n = 20 items) | O(n) |
| Store in module-level `FRUIT_LIST` | O(1) subsequent accesses |

### Per API request (`GET /fruit`)

Each active filter is applied as a single-pass list comprehension over the current result set:

```
results = list(FRUIT_LIST)          # O(n)  — shallow copy

if color:
    results = [f for f in results   # O(n)  — one pass
               if f["color"].lower() == color]

if in_season is not None:
    results = [f for f in results   # O(k)  — one pass over remaining k items
               if f["in_season"] == in_season]

if name:
    results = [f for f in results   # O(j)  — one pass over remaining j items
               if name in f["name"].lower()]
```

| Scenario | Time | Space |
|----------|------|-------|
| No filters (all 20 fruits) | O(n) for the copy | O(n) |
| One filter | O(n) copy + O(n) pass = O(n) | O(n) worst case |
| All three filters | O(n) + O(n) + O(k) + O(j) = **O(n)** | O(n) worst case |
| Best case (early filter eliminates all) | O(n) copy + O(n) first pass | O(1) — empty list |

With n = 20, every request completes in constant time in practice. The algorithm scales linearly if the dataset grows.

### Frontend (browser)
DOM rendering of k result cards is O(k). Filter tag rendering is O(number of active filters) = O(1) since there are only 3 possible filters.

---

## Project Structure

```
fruit-list-filter-app/
├── manage.py                   ← Django management entry point
├── requirements.txt            ← Python dependencies
├── pytest.ini                  ← pytest + Django settings pointer
├── fruitList.json              ← Static data source (20 fruits)
├── .gitignore
├── fruitproject/               ← Django project package
│   ├── __init__.py
│   ├── settings.py             ← App config, SQLite :memory: DB
│   ├── urls.py                 ← Root URL config (includes fruit.urls)
│   └── wsgi.py
└── fruit/                      ← Django application
    ├── __init__.py
    ├── apps.py
    ├── views.py                ← index view + fruit_api view
    ├── urls.py                 ← "" → index, "fruit" → fruit_api
    ├── templates/
    │   └── fruit/
    │       └── index.html      ← Full frontend (jQuery AJAX)
    └── tests/
        ├── __init__.py
        └── test_views.py       ← 17 pytest-django tests
```

---

## How to Run

> **Requirements**: Python 3.10 or later.

### Step 1 — Clone / navigate to the project

```bash
cd "/Users/macbookpro/Downloads/fruit-list-filter-app"
```

### Step 2 — Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Start the Django development server

```bash
python3 manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

The UI loads immediately — no build step, no compilation.

### Stopping the server

Press `Ctrl + C` in the terminal running the server.

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/` | Renders the HTML frontend |
| `GET` | `/fruit` | Returns all 20 fruits as a JSON array |
| `GET` | `/fruit?color=red` | Filter by exact color (case-insensitive) |
| `GET` | `/fruit?in_season=true` | Filter to in-season fruits only |
| `GET` | `/fruit?in_season=false` | Filter to out-of-season fruits only |
| `GET` | `/fruit?name=app` | Partial, case-insensitive name search |
| `GET` | `/fruit?color=red&in_season=true` | Combine any two filters |
| `GET` | `/fruit?color=red&in_season=true&name=app` | Combine all three filters |

**Example responses:**

```bash
# All fruits
curl http://127.0.0.1:8000/fruit

# Red fruits that are in season
curl "http://127.0.0.1:8000/fruit?color=red&in_season=true"

# Fruits whose name contains "berry"
curl "http://127.0.0.1:8000/fruit?name=berry"
```

Each fruit object in the response has the shape:
```json
{
  "name": "Apple",
  "color": "red",
  "in_season": true
}
```

---

## How to Run Tests

Make sure the virtual environment is activated, then run:

```bash
cd "/Users/macbookpro/Downloads/fruit-list-filter-app"
source venv/bin/activate
pytest -v
```

Expected output (all 17 tests, ~0.16 s):

```
fruit/tests/test_views.py::test_index_returns_200 PASSED
fruit/tests/test_views.py::test_index_contains_html PASSED
fruit/tests/test_views.py::test_fruit_api_returns_list PASSED
fruit/tests/test_views.py::test_fruit_api_total_count PASSED
fruit/tests/test_views.py::test_fruit_items_have_required_fields PASSED
fruit/tests/test_views.py::test_filter_by_color PASSED
fruit/tests/test_views.py::test_filter_by_color_case_insensitive PASSED
fruit/tests/test_views.py::test_filter_by_color_no_match PASSED
fruit/tests/test_views.py::test_filter_in_season_true PASSED
fruit/tests/test_views.py::test_filter_in_season_false PASSED
fruit/tests/test_views.py::test_in_season_counts_sum_to_total PASSED
fruit/tests/test_views.py::test_filter_by_name_partial PASSED
fruit/tests/test_views.py::test_filter_by_name_case_insensitive PASSED
fruit/tests/test_views.py::test_filter_by_name_no_match PASSED
fruit/tests/test_views.py::test_combined_color_and_season_filter PASSED
fruit/tests/test_views.py::test_combined_color_season_name_filter PASSED
fruit/tests/test_views.py::test_unknown_params_ignored PASSED

17 passed in 0.16s
```

### What is tested

| Category | Tests |
|----------|-------|
| HTML page | 200 status, correct content-type |
| Full list | JSON array returned, correct total count, all required fields present |
| Color filter | Exact match, case-insensitive, no-match returns empty list |
| In-season filter | `true` subset, `false` subset, both subsets sum to total |
| Name filter | Partial match, case-insensitive, no-match returns empty list |
| Combined filters | Two-param AND logic, three-param AND logic |
| Unknown params | Unrecognised query params are safely ignored |

---

## Edge Cases

### Filter behaviour

| Edge case | Behaviour |
|-----------|-----------|
| `?color=RED` or `?color=Red` | Normalised to lowercase — matches `red` fruits correctly |
| `?name=aPp` | Matches `Apple` **and** `Pineapple` (partial, case-insensitive substring) |
| `?color=turquoise` | Returns `[]` — no error, no crash |
| `?name=zzzzz` | Returns `[]` — no error, no crash |
| `?in_season=yes` or `?in_season=1` | Neither `"true"` nor `"false"` exactly — filter is **ignored**, all fruits returned |
| Multiple filters | Applied as AND logic — every active filter must match |
| No query params | Returns the full list of 20 fruits |

### Frontend / UX edge cases

| Edge case | Behaviour |
|-----------|-----------|
| Rapid typing in the name field | A 300 ms debounce delays the AJAX call; if another keystroke arrives before the delay expires, the timer resets |
| XHR race condition | If a previous request is still in-flight when filters change, `activeXHR.abort()` cancels it — only the latest request's results are rendered |
| Filter tag removal | Clicking × on an active filter tag removes that single filter and re-fetches without rebuilding the whole UI |
| URL sharing | Filters are written to the querystring via `history.pushState()`; opening the URL in a new tab or sharing it restores the exact same filter state |
| Browser back/forward | `popstate` event listener reads the URL and re-applies filters, so back/forward navigation works as expected |
| XSS in fruit names | Fruit names are inserted via jQuery's `.text()` method, which escapes HTML entities — malicious content in the JSON cannot inject scripts |

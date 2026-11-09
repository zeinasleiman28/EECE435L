# Lab 5 – Postman and APIs

**EECE 435L – Software Tools Lab** · Zeina Sleiman

Flask REST API over a SQLite `users` table (CRUD). Used again as the base project for Lab 7 (pytest) and Lab 8 (Docker).

| Method | Endpoint | Function |
|---|---|---|
| GET | `/api/users` | `get_users()` |
| GET | `/api/users/<user_id>` | `get_user_by_id()` |
| POST | `/api/users/add` | `insert_user()` |
| PUT | `/api/users/update` | `update_user()` |
| DELETE | `/api/users/delete/<user_id>` | `delete_user()` |

## Run

```powershell
cd Lab5
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

First run creates `database.db` and seeds it with 3 users (`INITIAL_USERS` in `app.py`). Open http://127.0.0.1:5000/api/users in the browser to check.

`DATABASE` env var overrides the DB file path (used by the Lab 7 tests), `PORT` overrides the port (used by Lab 8).

# Lab 7 – Python testing (pytest)

**EECE 435L – Software Tools Lab** · Zeina Sleiman

`Lab7-Zeina-Sleiman/` = the Lab 5 user-management app (`app.py`) + `test_user_Zeina_Sleiman.py`, a pytest suite covering the 10 required functions:

| # | Function under test | Tests |
|---|---|---|
| 1 | DB created with the initial users on first run | `test_db_created_with_initial_users`, `test_create_db_table_second_run_does_not_duplicate_users` |
| 2 | `insert_user()` | `test_insert_user`, `test_insert_user_missing_field_returns_empty` |
| 3 | `get_users()` | `test_get_users` |
| 4 | `get_user_by_id()` | `test_get_user_by_id`, `test_get_user_by_id_not_found` |
| 5 | `update_user()` | `test_update_user`, `test_update_user_nonexistent_returns_empty` |
| 6 | `delete_user()` | `test_delete_user` |
| 7 | `api_get_user()` | `test_api_get_users`, `test_api_get_user`, `test_api_get_user_not_found` |
| 8 | `api_add_user()` | `test_api_add_user` |
| 9 | `api_update_user()` | `test_api_update_user` |
| 10 | `api_delete_user()` | `test_api_delete_user` |

API tests check both the HTTP status code and the JSON body, and then re-read the DB to confirm the change was really persisted.

## How the tests stay isolated

- `fresh_db` is an `autouse` fixture: before every test it points `app.DATABASE` at a new file in pytest's `tmp_path` (via `monkeypatch`) and calls `create_db_table()`. Each test therefore starts from the same "first run" state and never touches the real `database.db`.
- `client` returns `app.test_client()`, Flask's built-in fake HTTP client, so no server has to be running.

## Run

```powershell
cd Lab7\Lab7-Zeina-Sleiman
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -v
```

Expected: `16 passed`.

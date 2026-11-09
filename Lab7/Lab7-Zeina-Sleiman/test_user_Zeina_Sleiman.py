"""Lab 7 - pytest suite for the Lab 5 user management app.

EECE 435L - Software Tools Lab - Zeina Sleiman

Run:  pytest -v
"""
import os
import pytest

import app as users_app
from app import (
    app, create_db_table, insert_user, get_users, get_user_by_id,
    update_user, delete_user, INITIAL_USERS,
)


NEW_USER = {
    "name": "Ali Hassan",
    "email": "ali.hassan@example.com",
    "phone": "0096171234567",
    "address": "Hamra Street, Beirut",
    "country": "Lebanon",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    """Give every test its own brand-new SQLite file.

    autouse=True  -> runs before each test without being listed as an argument.
    tmp_path      -> pytest built-in fixture: a unique temporary directory.
    monkeypatch   -> swaps app.DATABASE for this test only, then restores it.
    """
    db_file = tmp_path / "test_database.db"
    monkeypatch.setattr(users_app, "DATABASE", str(db_file))
    create_db_table()          # "first run" -> table + initial users
    yield
    if db_file.exists():
        os.remove(db_file)


@pytest.fixture
def client():
    """Flask test client: sends HTTP requests to the app without a server."""
    app.config["TESTING"] = True
    return app.test_client()


# ---------------------------------------------------------------------------
# 1. Database created with the specified users on first run
# ---------------------------------------------------------------------------

def test_db_created_with_initial_users():
    users = get_users()
    assert len(users) == len(INITIAL_USERS)
    assert [u["name"] for u in users] == [u["name"] for u in INITIAL_USERS]
    assert [u["email"] for u in users] == [u["email"] for u in INITIAL_USERS]


def test_create_db_table_second_run_does_not_duplicate_users():
    assert create_db_table() is False         # table already exists
    assert len(get_users()) == len(INITIAL_USERS)


# ---------------------------------------------------------------------------
# 2. insert_user()
# ---------------------------------------------------------------------------

def test_insert_user():
    inserted = insert_user(NEW_USER)
    assert inserted["user_id"] == len(INITIAL_USERS) + 1
    for key in NEW_USER:
        assert inserted[key] == NEW_USER[key]
    assert len(get_users()) == len(INITIAL_USERS) + 1


def test_insert_user_missing_field_returns_empty():
    bad_user = {"name": "No Email"}
    assert insert_user(bad_user) == {}
    assert len(get_users()) == len(INITIAL_USERS)


# ---------------------------------------------------------------------------
# 3. get_users()
# ---------------------------------------------------------------------------

def test_get_users():
    insert_user(NEW_USER)
    users = get_users()
    assert isinstance(users, list)
    assert len(users) == len(INITIAL_USERS) + 1
    assert set(users[0].keys()) == {"user_id", "name", "email", "phone", "address", "country"}


# ---------------------------------------------------------------------------
# 4. get_user_by_id()
# ---------------------------------------------------------------------------

def test_get_user_by_id():
    user = get_user_by_id(1)
    assert user["user_id"] == 1
    assert user["name"] == INITIAL_USERS[0]["name"]


def test_get_user_by_id_not_found():
    assert get_user_by_id(9999) == {}


# ---------------------------------------------------------------------------
# 5. update_user()
# ---------------------------------------------------------------------------

def test_update_user():
    updated_data = dict(NEW_USER, user_id=1, name="Zeina S. Updated")
    updated = update_user(updated_data)
    assert updated == updated_data
    assert get_user_by_id(1)["name"] == "Zeina S. Updated"


def test_update_user_nonexistent_returns_empty():
    assert update_user(dict(NEW_USER, user_id=9999)) == {}


# ---------------------------------------------------------------------------
# 6. delete_user()
# ---------------------------------------------------------------------------

def test_delete_user():
    message = delete_user(1)
    assert message["status"] == "User deleted successfully"
    assert get_user_by_id(1) == {}
    assert len(get_users()) == len(INITIAL_USERS) - 1


# ---------------------------------------------------------------------------
# 7. api_get_user()  (GET /api/users and GET /api/users/<id>)
# ---------------------------------------------------------------------------

def test_api_get_users(client):
    response = client.get("/api/users")
    data = response.get_json()
    assert response.status_code == 200
    assert len(data) == len(INITIAL_USERS)
    assert "Zeina Sleiman" in str(response.data)


def test_api_get_user(client):
    response = client.get("/api/users/2")
    data = response.get_json()
    assert response.status_code == 200
    assert data["user_id"] == 2
    assert data["name"] == INITIAL_USERS[1]["name"]


def test_api_get_user_not_found(client):
    response = client.get("/api/users/9999")
    assert response.status_code == 200
    assert response.get_json() == {}


# ---------------------------------------------------------------------------
# 8. api_add_user()  (POST /api/users/add)
# ---------------------------------------------------------------------------

def test_api_add_user(client):
    response = client.post("/api/users/add", json=NEW_USER)
    data = response.get_json()
    assert response.status_code == 200
    assert data["user_id"] == len(INITIAL_USERS) + 1
    for key in NEW_USER:
        assert data[key] == NEW_USER[key]
    # really stored, not just echoed back
    assert get_user_by_id(data["user_id"])["email"] == NEW_USER["email"]


# ---------------------------------------------------------------------------
# 9. api_update_user()  (PUT /api/users/update)
# ---------------------------------------------------------------------------

def test_api_update_user(client):
    payload = dict(NEW_USER, user_id=3, country="France")
    response = client.put("/api/users/update", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert data == payload
    assert get_user_by_id(3)["country"] == "France"


# ---------------------------------------------------------------------------
# 10. api_delete_user()  (DELETE /api/users/delete/<id>)
# ---------------------------------------------------------------------------

def test_api_delete_user(client):
    response = client.delete("/api/users/delete/2")
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == "User deleted successfully"
    assert get_user_by_id(2) == {}
    assert 2 not in [u["user_id"] for u in client.get("/api/users").get_json()]

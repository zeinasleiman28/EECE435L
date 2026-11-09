#!/usr/bin/python
"""Lab 5 - Flask + SQLite user management REST API.

EECE 435L - Software Tools Lab - Zeina Sleiman

Database functions (connect_to_db, create_db_table, insert_user, get_users,
get_user_by_id, update_user, delete_user) are exposed through the REST
endpoints at the bottom of the file.
"""
import os
import sqlite3

from flask import Flask, request, jsonify
from flask_cors import CORS

# Path of the SQLite file. Overridable with the DATABASE env var so tests
# can point the app at a temporary database instead of the real one.
DATABASE = os.environ.get("DATABASE", "database.db")

# Users inserted the first time the app runs (table did not exist yet).
INITIAL_USERS = [
    {"name": "Zeina Sleiman", "email": "zhs13@mail.aub.edu",
     "phone": "0096170000001", "address": "Bliss Street, Beirut", "country": "Lebanon"},
    {"name": "John Doe", "email": "jondoe@gmail.com",
     "phone": "067765434567", "address": "John Doe Street, Innsbruck", "country": "Austria"},
    {"name": "Jane Smith", "email": "jane.smith@example.com",
     "phone": "0044770000002", "address": "Baker Street, London", "country": "United Kingdom"},
]


# ---------------------------------------------------------------------------
# Database layer
# ---------------------------------------------------------------------------

def connect_to_db():
    conn = sqlite3.connect(DATABASE)
    return conn


def create_db_table():
    """Create the users table and seed it with INITIAL_USERS on first run."""
    created = False
    try:
        conn = connect_to_db()
        conn.execute('''
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                country TEXT NOT NULL
            );
        ''')
        conn.commit()
        created = True
        print("User table created successfully")
    except sqlite3.OperationalError:
        print("User table creation failed - Maybe table already exists")
    finally:
        conn.close()

    if created:
        for user in INITIAL_USERS:
            insert_user(user)
    return created


def insert_user(user):
    inserted_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email, phone, address, country) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (user['name'], user['email'], user['phone'],
                     user['address'], user['country']))
        conn.commit()
        inserted_user = get_user_by_id(cur.lastrowid)
    except Exception:
        conn.rollback()
    finally:
        conn.close()

    return inserted_user


def _row_to_user(row):
    return {
        "user_id": row["user_id"],
        "name": row["name"],
        "email": row["email"],
        "phone": row["phone"],
        "address": row["address"],
        "country": row["country"],
    }


def get_users():
    users = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        users = [_row_to_user(i) for i in rows]
    except Exception:
        users = []
    finally:
        conn.close()

    return users


def get_user_by_id(user_id):
    user = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        user = _row_to_user(row)
    except Exception:
        user = {}
    finally:
        conn.close()

    return user


def update_user(user):
    updated_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET name = ?, email = ?, phone = ?, "
                    "address = ?, country = ? WHERE user_id = ?",
                    (user["name"], user["email"], user["phone"],
                     user["address"], user["country"], user["user_id"]))
        conn.commit()
        updated_user = get_user_by_id(user["user_id"])
    except Exception:
        conn.rollback()
        updated_user = {}
    finally:
        conn.close()

    return updated_user


def delete_user(user_id):
    message = {}
    try:
        conn = connect_to_db()
        conn.execute("DELETE from users WHERE user_id = ?", (user_id,))
        conn.commit()
        message["status"] = "User deleted successfully"
    except Exception:
        conn.rollback()
        message["status"] = "Cannot delete user"
    finally:
        conn.close()

    return message


# ---------------------------------------------------------------------------
# REST API
# ---------------------------------------------------------------------------

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/api/users', methods=['GET'])
def api_get_users():
    return jsonify(get_users())


@app.route('/api/users/<user_id>', methods=['GET'])
def api_get_user(user_id):
    return jsonify(get_user_by_id(user_id))


@app.route('/api/users/add', methods=['POST'])
def api_add_user():
    user = request.get_json()
    return jsonify(insert_user(user))


@app.route('/api/users/update', methods=['PUT'])
def api_update_user():
    user = request.get_json()
    return jsonify(update_user(user))


@app.route('/api/users/delete/<user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    return jsonify(delete_user(user_id))


if __name__ == "__main__":
    create_db_table()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

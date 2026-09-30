import os
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def init_db():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS todos "
            "(id SERIAL PRIMARY KEY, title TEXT NOT NULL)"
        )


@app.route("/health")
def health():
    return "ok"


@app.route("/todos", methods=["POST"])
def add_todo():
    title = request.get_json().get("title")
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO todos (title) VALUES (%s) RETURNING id", (title,))
        todo_id = cur.fetchone()[0]
    return jsonify({"id": todo_id, "title": title}), 201


@app.route("/todos")
def list_todos():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, title FROM todos ORDER BY id")
        rows = cur.fetchall()
    return jsonify([{"id": r[0], "title": r[1]} for r in rows])


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)

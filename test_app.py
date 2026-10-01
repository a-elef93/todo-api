from unittest.mock import MagicMock

import app as app_module


def make_fake_conn(fetchone=None, fetchall=None):
    conn = MagicMock()
    cur = conn.__enter__.return_value.cursor.return_value.__enter__.return_value
    if fetchone is not None:
        cur.fetchone.return_value = fetchone
    if fetchall is not None:
        cur.fetchall.return_value = fetchall
    return conn, cur


def test_health():
    client = app_module.app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.data == b"ok"


def test_add_todo(monkeypatch):
    conn, cur = make_fake_conn(fetchone=(1,))
    monkeypatch.setattr(app_module, "get_conn", lambda: conn)

    client = app_module.app.test_client()
    response = client.post("/todos", json={"title": "buy milk"})

    assert response.status_code == 200
    assert response.get_json() == {"id": 1, "title": "buy milk"}
    cur.execute.assert_called_once()


def test_list_todos(monkeypatch):
    conn, cur = make_fake_conn(fetchall=[(1, "a"), (2, "b")])
    monkeypatch.setattr(app_module, "get_conn", lambda: conn)

    client = app_module.app.test_client()
    response = client.get("/todos")

    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 1, "title": "a"},
        {"id": 2, "title": "b"},
    ]

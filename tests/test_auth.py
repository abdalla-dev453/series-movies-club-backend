from tests.helpers import signup, auth_headers


def test_signup_creates_user(client):
    resp = signup(client)
    assert resp.status_code == 201
    assert resp.get_json()["user"]["username"] == "alice"


def test_signup_rejects_duplicate_username(client):
    signup(client)
    resp = signup(client, email="other@example.com")
    assert resp.status_code == 409


def test_signup_rejects_short_password(client):
    resp = client.post(
        "/api/auth/signup",
        json={"username": "bob", "email": "bob@example.com", "password": "short"},
    )
    assert resp.status_code == 400


def test_login_succeeds_with_correct_credentials(client):
    signup(client)
    resp = client.post("/api/auth/login", json={"username": "alice", "password": "password123"})
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


def test_login_rejects_wrong_password(client):
    signup(client)
    resp = client.post("/api/auth/login", json={"username": "alice", "password": "wrongpass"})
    assert resp.status_code == 401


def test_logout_revokes_token(client):
    resp = signup(client)
    headers = auth_headers(resp)

    logout_resp = client.post("/api/auth/logout", headers=headers)
    assert logout_resp.status_code == 200

    me_resp = client.put("/api/users/1", headers=headers, json={"bio": "hi"})
    assert me_resp.status_code == 401


def test_list_users_excludes_current_user(client):
    alice = signup(client, username="alice", email="alice@example.com", password="password123")
    signup(client, username="bob", email="bob@example.com", password="password123")

    alice_headers = auth_headers(alice)
    resp = client.get("/api/users", headers=alice_headers)

    assert resp.status_code == 200
    users = resp.get_json()["items"]
    assert [u["username"] for u in users] == ["bob"]

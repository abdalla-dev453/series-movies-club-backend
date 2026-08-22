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
        "/signup",
        json={"username": "bob", "email": "bob@example.com", "password": "short"},
    )
    assert resp.status_code == 400


def test_login_succeeds_with_correct_credentials(client):
    signup(client)
    resp = client.post("/login", json={"username": "alice", "password": "password123"})
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


def test_login_rejects_wrong_password(client):
    signup(client)
    resp = client.post("/login", json={"username": "alice", "password": "wrongpass"})
    assert resp.status_code == 401


def test_logout_revokes_token(client):
    resp = signup(client)
    headers = auth_headers(resp)

    logout_resp = client.post("/logout", headers=headers)
    assert logout_resp.status_code == 200

    me_resp = client.put("/users/1", headers=headers, json={"bio": "hi"})
    assert me_resp.status_code == 401
"""Small request helpers shared across test modules -- not fixtures, just
functions, kept out of conftest.py to keep that file fixture-only."""


def signup(client, username="alice", email="alice@example.com", password="password123"):
    return client.post(
        "/signup", json={"username": username, "email": email, "password": password}
    )


def auth_headers(signup_response):
    token = signup_response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def signup_and_login(client, **kwargs):
    resp = signup(client, **kwargs)
    return resp.get_json()["user"], auth_headers(resp)

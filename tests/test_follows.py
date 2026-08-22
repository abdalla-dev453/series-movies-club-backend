from tests.helpers import signup_and_login


def test_cannot_follow_self(client):
    user, headers = signup_and_login(client)
    resp = client.post(f"/users/{user['id']}/follow", headers=headers)
    assert resp.status_code == 400


def test_duplicate_follow_is_rejected(client):
    _, headers_a = signup_and_login(client, username="alice", email="a@example.com")
    user_b, _ = signup_and_login(client, username="bob", email="b@example.com")

    client.post(f"/users/{user_b['id']}/follow", headers=headers_a)
    resp = client.post(f"/users/{user_b['id']}/follow", headers=headers_a)
    assert resp.status_code == 409


def test_follow_then_unfollow(client):
    _, headers_a = signup_and_login(client, username="alice", email="a@example.com")
    user_b, _ = signup_and_login(client, username="bob", email="b@example.com")

    client.post(f"/users/{user_b['id']}/follow", headers=headers_a)
    resp = client.delete(f"/users/{user_b['id']}/unfollow", headers=headers_a)
    assert resp.status_code == 204


def test_followers_list_reflects_follow(client):
    user_a, headers_a = signup_and_login(client, username="alice", email="a@example.com")
    user_b, _ = signup_and_login(client, username="bob", email="b@example.com")

    client.post(f"/users/{user_b['id']}/follow", headers=headers_a)
    resp = client.get(f"/users/{user_b['id']}/followers")
    usernames = [u["username"] for u in resp.get_json()]
    assert user_a["username"] in usernames

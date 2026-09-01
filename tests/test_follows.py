from tests.helpers import signup_and_login


def test_update_profile_allows_username_and_avatar_url(client):
    user, headers = signup_and_login(client)

    resp = client.put(
        f"/api/users/{user['id']}",
        headers=headers,
        json={
            "username": "updated_user",
            "avatar_url": "https://example.com/avatar.jpg",
            "bio": "Updated bio",
        },
    )

    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["username"] == "updated_user"
    assert payload["avatar_url"] == "https://example.com/avatar.jpg"
    assert payload["bio"] == "Updated bio"


def test_cannot_follow_self(client):
    user, headers = signup_and_login(client)
    resp = client.post(f"/api/users/{user['id']}/follow", headers=headers)
    assert resp.status_code == 400


def test_duplicate_follow_is_rejected(client):
    _, headers_a = signup_and_login(
        client, username="alice", email="a@example.com")
    user_b, _ = signup_and_login(client, username="bob", email="b@example.com")

    client.post(f"/api/users/{user_b['id']}/follow", headers=headers_a)
    resp = client.post(f"/api/users/{user_b['id']}/follow", headers=headers_a)
    assert resp.status_code == 409


def test_follow_then_unfollow(client):
    _, headers_a = signup_and_login(
        client, username="alice", email="a@example.com")
    user_b, _ = signup_and_login(client, username="bob", email="b@example.com")

    client.post(f"/api/users/{user_b['id']}/follow", headers=headers_a)
    resp = client.delete(
        f"/api/users/{user_b['id']}/unfollow", headers=headers_a)
    assert resp.status_code == 204


def test_followers_list_reflects_follow(client):
    user_a, headers_a = signup_and_login(
        client, username="alice", email="a@example.com")
    user_b, _ = signup_and_login(client, username="bob", email="b@example.com")

    client.post(f"/api/users/{user_b['id']}/follow", headers=headers_a)
    resp = client.get(f"/api/users/{user_b['id']}/followers")
    usernames = [u["username"] for u in resp.get_json()]
    assert user_a["username"] in usernames


def test_mutual_followers_are_visible_to_each_user(client):
    user_a, headers_a = signup_and_login(
        client, username="alice", email="a@example.com")
    user_b, headers_b = signup_and_login(
        client, username="bob", email="b@example.com")

    client.post(f"/api/users/{user_b['id']}/follow", headers=headers_a)
    client.post(f"/api/users/{user_a['id']}/follow", headers=headers_b)

    mutual_a = client.get(f"/api/users/{user_a['id']}/mutual")
    mutual_b = client.get(f"/api/users/{user_b['id']}/mutual")

    usernames_a = [u["username"] for u in mutual_a.get_json()]
    usernames_b = [u["username"] for u in mutual_b.get_json()]

    assert user_b["username"] in usernames_a
    assert user_a["username"] in usernames_b

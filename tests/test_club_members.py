from tests.helpers import signup_and_login


def create_club(client, headers, name="Sci-Fi Fans", genre="Sci-Fi"):
    resp = client.post("/clubs", headers=headers, json={"name": name, "genre": genre})
    return resp.get_json()["id"]


def test_user_can_join_club(client):
    _, headers_a = signup_and_login(client, username="alice", email="a@example.com")
    club_id = create_club(client, headers_a)

    _, headers_b = signup_and_login(client, username="bob", email="b@example.com")
    resp = client.post(f"/clubs/{club_id}/join", headers=headers_b)
    assert resp.status_code == 201


def test_duplicate_join_is_rejected(client):
    _, headers_a = signup_and_login(client, username="alice", email="a@example.com")
    club_id = create_club(client, headers_a)

    resp = client.post(f"/clubs/{club_id}/join", headers=headers_a)
    assert resp.status_code == 409


def test_last_admin_cannot_be_demoted(client):
    user_a, headers_a = signup_and_login(client, username="alice", email="a@example.com")
    club_id = create_club(client, headers_a)

    resp = client.put(
        f"/clubs/{club_id}/members/{user_a['id']}",
        headers=headers_a,
        json={"role": "member"},
    )
    assert resp.status_code == 400


def test_last_admin_cannot_leave(client):
    _, headers_a = signup_and_login(client, username="alice", email="a@example.com")
    club_id = create_club(client, headers_a)

    resp = client.delete(f"/clubs/{club_id}/leave", headers=headers_a)
    assert resp.status_code == 400

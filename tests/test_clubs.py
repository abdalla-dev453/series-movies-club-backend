from tests.helpers import signup_and_login


def create_club(client, headers, name="Horror Fans", genre="Horror"):
    return client.post("/api/clubs", headers=headers, json={"name": name, "genre": genre})


def test_create_club_makes_creator_an_admin(client):
    _, headers = signup_and_login(client)
    resp = create_club(client, headers)
    assert resp.status_code == 201
    club_id = resp.get_json()["id"]

    members = client.get(f"/api/clubs/{club_id}/members").get_json()
    assert len(members) == 1
    assert members[0]["role"] == "admin"


def test_list_clubs_is_paginated(client):
    _, headers = signup_and_login(client)
    for i in range(3):
        create_club(client, headers, name=f"Club {i}", genre="Drama")

    resp = client.get("/api/clubs?per_page=2", headers=headers)
    data = resp.get_json()
    assert len(data["items"]) == 2
    assert data["total_items"] == 3
    assert data["total_pages"] == 2


def test_only_admin_can_update_club(client):
    _, headers_a = signup_and_login(client, username="alice", email="a@example.com")
    _, headers_b = signup_and_login(client, username="bob", email="b@example.com")

    resp = create_club(client, headers_a)
    club_id = resp.get_json()["id"]

    forbidden = client.put(f"/api/clubs/{club_id}", headers=headers_b, json={"name": "Hijacked"})
    assert forbidden.status_code == 403


def test_create_club_requires_auth(client):
    resp = client.post("/api/clubs", json={"name": "No Auth", "genre": "Comedy"})
    assert resp.status_code == 401

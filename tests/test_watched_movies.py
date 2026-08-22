from tests.helpers import signup_and_login


def test_add_watched_movie(client):
    _, headers = signup_and_login(client)
    resp = client.post(
        "/watched",
        headers=headers,
        json={"movie_title": "Parasite", "watched_date": "2024-01-15", "personal_rating": 5},
    )
    assert resp.status_code == 201
    assert resp.get_json()["movie_title"] == "Parasite"


def test_invalid_date_format_is_rejected(client):
    _, headers = signup_and_login(client)
    resp = client.post(
        "/watched",
        headers=headers,
        json={"movie_title": "Parasite", "watched_date": "01/15/2024"},
    )
    assert resp.status_code == 400


def test_cannot_delete_another_users_watched_entry(client):
    _, headers_a = signup_and_login(client, username="alice", email="a@example.com")
    entry_resp = client.post("/watched", headers=headers_a, json={"movie_title": "Dune"})
    entry_id = entry_resp.get_json()["id"]

    _, headers_b = signup_and_login(client, username="bob", email="b@example.com")
    resp = client.delete(f"/watched/{entry_id}", headers=headers_b)
    assert resp.status_code == 403


def test_get_missing_watched_entry_is_404(client):
    _, headers = signup_and_login(client)
    resp = client.delete("/watched/999", headers=headers)
    assert resp.status_code == 404
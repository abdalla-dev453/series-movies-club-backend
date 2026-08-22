from tests.helpers import signup_and_login


def create_club(client, headers, name="Comedy Fans", genre="Comedy"):
    resp = client.post("/clubs", headers=headers, json={"name": name, "genre": genre})
    return resp.get_json()["id"]


def test_create_personal_post(client):
    _, headers = signup_and_login(client)
    resp = client.post("/posts", headers=headers, json={"movie_title": "Inside Out"})
    assert resp.status_code == 201
    assert resp.get_json()["club_id"] is None


def test_non_member_cannot_post_into_club(client):
    _, headers_a = signup_and_login(client, username="alice", email="a@example.com")
    club_id = create_club(client, headers_a)

    _, headers_b = signup_and_login(client, username="bob", email="b@example.com")
    resp = client.post(
        "/posts", headers=headers_b, json={"movie_title": "Up", "club_id": club_id}
    )
    assert resp.status_code == 403


def test_club_admin_can_delete_others_post(client):
    _, headers_a = signup_and_login(client, username="alice", email="a@example.com")
    club_id = create_club(client, headers_a)

    _, headers_b = signup_and_login(client, username="bob", email="b@example.com")
    client.post(f"/clubs/{club_id}/join", headers=headers_b)
    post_resp = client.post(
        "/posts", headers=headers_b, json={"movie_title": "Coco", "club_id": club_id}
    )
    post_id = post_resp.get_json()["id"]

    resp = client.delete(f"/posts/{post_id}", headers=headers_a)
    assert resp.status_code == 204


def test_get_missing_post_is_404(client):
    resp = client.get("/posts/999")
    assert resp.status_code == 404
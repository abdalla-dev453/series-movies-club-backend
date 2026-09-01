from tests.helpers import signup_and_login


def create_club(client, headers, name="Film Club", genre="Drama"):
    resp = client.post("/api/clubs", headers=headers,
                       json={"name": name, "genre": genre})
    return resp.get_json()["id"]


def create_post(client, headers, title="The Matrix"):
    resp = client.post("/api/posts", headers=headers,
                       json={"movie_title": title})
    return resp.get_json()["id"]


def test_cannot_review_own_post(client):
    _, headers = signup_and_login(client)
    post_id = create_post(client, headers)

    resp = client.post("/api/reviews", headers=headers,
                       json={"post_id": post_id, "rating": 5})
    assert resp.status_code == 403


def test_duplicate_review_is_rejected(client):
    _, headers_a = signup_and_login(
        client, username="alice", email="a@example.com")
    post_id = create_post(client, headers_a)

    _, headers_b = signup_and_login(
        client, username="bob", email="b@example.com")
    client.post("/api/reviews", headers=headers_b,
                json={"post_id": post_id, "rating": 4})
    resp = client.post("/api/reviews", headers=headers_b,
                       json={"post_id": post_id, "rating": 5})
    assert resp.status_code == 409


def test_invalid_rating_is_rejected(client):
    _, headers_a = signup_and_login(
        client, username="alice", email="a@example.com")
    post_id = create_post(client, headers_a)

    _, headers_b = signup_and_login(
        client, username="bob", email="b@example.com")
    resp = client.post("/api/reviews", headers=headers_b,
                       json={"post_id": post_id, "rating": 9})
    assert resp.status_code == 400


def test_author_can_edit_own_review(client):
    _, headers_a = signup_and_login(
        client, username="alice", email="a@example.com")
    post_id = create_post(client, headers_a)

    _, headers_b = signup_and_login(
        client, username="bob", email="b@example.com")
    review_resp = client.post(
        "/api/reviews", headers=headers_b, json={"post_id": post_id, "rating": 3}
    )
    review_id = review_resp.get_json()["id"]

    resp = client.put(f"/api/reviews/{review_id}",
                      headers=headers_b, json={"rating": 5})
    assert resp.status_code == 200
    assert resp.get_json()["rating"] == 5


def test_review_payload_includes_author_club_when_member(client):
    _, headers_a = signup_and_login(
        client, username="alice", email="alice@example.com")
    club_id = create_club(
        client, headers_a, name="Sci-Fi Night", genre="Sci-Fi")

    _, headers_b = signup_and_login(
        client, username="bob", email="bob@example.com")
    client.post(f"/api/clubs/{club_id}/join", headers=headers_b)

    post_id = client.post(
        "/api/posts",
        headers=headers_a,
        json={"movie_title": "Arrival", "club_id": club_id},
    ).get_json()["id"]

    review_resp = client.post(
        "/api/reviews",
        headers=headers_b,
        json={"post_id": post_id, "rating": 4, "comment_text": "Great film."},
    )

    assert review_resp.status_code == 201
    payload = review_resp.get_json()
    assert payload["club"]["name"] == "Sci-Fi Night"

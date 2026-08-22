from tests.helpers import signup_and_login


def create_post(client, headers, title="The Matrix"):
    resp = client.post("/posts", headers=headers, json={"movie_title": title})
    return resp.get_json()["id"]


def test_cannot_review_own_post(client):
    _, headers = signup_and_login(client)
    post_id = create_post(client, headers)

    resp = client.post("/reviews", headers=headers, json={"post_id": post_id, "rating": 5})
    assert resp.status_code == 403


def test_duplicate_review_is_rejected(client):
    _, headers_a = signup_and_login(client, username="alice", email="a@example.com")
    post_id = create_post(client, headers_a)

    _, headers_b = signup_and_login(client, username="bob", email="b@example.com")
    client.post("/reviews", headers=headers_b, json={"post_id": post_id, "rating": 4})
    resp = client.post("/reviews", headers=headers_b, json={"post_id": post_id, "rating": 5})
    assert resp.status_code == 409


def test_invalid_rating_is_rejected(client):
    _, headers_a = signup_and_login(client, username="alice", email="a@example.com")
    post_id = create_post(client, headers_a)

    _, headers_b = signup_and_login(client, username="bob", email="b@example.com")
    resp = client.post("/reviews", headers=headers_b, json={"post_id": post_id, "rating": 9})
    assert resp.status_code == 400


def test_author_can_edit_own_review(client):
    _, headers_a = signup_and_login(client, username="alice", email="a@example.com")
    post_id = create_post(client, headers_a)

    _, headers_b = signup_and_login(client, username="bob", email="b@example.com")
    review_resp = client.post(
        "/reviews", headers=headers_b, json={"post_id": post_id, "rating": 3}
    )
    review_id = review_resp.get_json()["id"]

    resp = client.put(f"/reviews/{review_id}", headers=headers_b, json={"rating": 5})
    assert resp.status_code == 200
    assert resp.get_json()["rating"] == 5
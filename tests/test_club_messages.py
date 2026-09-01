from tests.helpers import signup_and_login


def create_club(client, headers, name="Chat Club", genre="Drama"):
    resp = client.post("/api/clubs", headers=headers,
                       json={"name": name, "genre": genre})
    return resp.get_json()["id"]


def test_members_can_post_and_delete_their_own_message(client):
    _, headers_a = signup_and_login(
        client, username="alice", email="alice@example.com")
    club_id = create_club(client, headers_a)

    _, headers_b = signup_and_login(
        client, username="bob", email="bob@example.com")
    client.post(f"/api/clubs/{club_id}/join", headers=headers_b)

    create_resp = client.post(
        f"/api/clubs/{club_id}/messages",
        headers=headers_b,
        json={"message": "Hello club!"},
    )
    assert create_resp.status_code == 201
    payload = create_resp.get_json()
    assert payload["message"] == "Hello club!"

    list_resp = client.get(f"/api/clubs/{club_id}/messages", headers=headers_b)
    assert list_resp.status_code == 200
    assert list_resp.get_json()[0]["message"] == "Hello club!"

    delete_resp = client.delete(
        f"/api/clubs/{club_id}/messages/{payload['id']}",
        headers=headers_b,
    )
    assert delete_resp.status_code == 204


def test_admin_can_delete_members_message(client):
    _, headers_a = signup_and_login(
        client, username="alice", email="alice@example.com")
    club_id = create_club(client, headers_a)

    _, headers_b = signup_and_login(
        client, username="bob", email="bob@example.com")
    client.post(f"/api/clubs/{club_id}/join", headers=headers_b)

    message_resp = client.post(
        f"/api/clubs/{club_id}/messages",
        headers=headers_b,
        json={"message": "I am a member."},
    )
    message_id = message_resp.get_json()["id"]

    delete_resp = client.delete(
        f"/api/clubs/{club_id}/messages/{message_id}",
        headers=headers_a,
    )
    assert delete_resp.status_code == 204

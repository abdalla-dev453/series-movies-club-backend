from tests.helpers import signup_and_login


class FakeResponse:
    def __init__(self, payload, status=200, headers=None):
        self.payload, self.status_code = payload, status
        self.headers = headers or {}

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.responses.pop(0)


def test_watch_route_maps_youtube_trailers_and_region_providers(client, app):
    _, headers = signup_and_login(client)
    fake = FakeSession([
        FakeResponse({"id": 12, "title": "Example"}),
        FakeResponse({"results": [
            {"id": "bad", "key": "", "site": "YouTube", "type": "Trailer", "official": True},
            {"id": "other", "key": "other-key", "site": "Vimeo", "type": "Trailer", "official": True},
            {"id": "teaser", "name": "Teaser", "key": "teaser-key", "site": "YouTube", "type": "Teaser", "official": True},
            {"id": "trailer", "name": "Official Trailer", "key": "trailer-key", "site": "YouTube", "type": "Trailer", "official": True},
        ]}),
        FakeResponse({"results": {"KE": {"flatrate": [{"provider_id": 8, "provider_name": "Netflix", "logo_path": "/n.jpg", "link": "https://netflix.example"}], "rent": [], "buy": []}}}),
    ])
    from app.routes import watch_routes
    watch_routes.watch_service.session = fake
    try:
        response = client.get("/api/movies/12/watch?country=KE", headers=headers)
    finally:
        watch_routes.watch_service.session = __import__("requests")
    assert response.status_code == 200
    data = response.get_json()
    assert data["primary_trailer"]["key"] == "trailer-key"
    assert [video["type"] for video in data["videos"]] == ["Trailer", "Teaser"]
    provider = data["watch_providers"]["stream"][0]
    assert provider["deep_link"] == "https://www.themoviedb.org/movie/12/watch?locale=KE"
    assert "netflix.example" not in response.get_data(as_text=True)


def test_watch_endpoints_require_authentication(client):
    response = client.get("/api/movies/12/watch/providers")
    assert response.status_code == 401


def test_invalid_country_rejected(client):
    _, headers = signup_and_login(client)
    response = client.get("/api/movies/12/watch/providers?country=usa", headers=headers)
    assert response.status_code == 400


def test_provider_cache_key_includes_country_and_ttl():
    from app.services.tmdb_watch_service import TMDBWatchService

    class Cache:
        def __init__(self): self.values, self.ttls = {}, {}
        def get(self, key): return self.values.get(key)
        def set(self, key, value, ex=None): self.values[key], self.ttls[key] = value, ex

    cache = Cache()
    fake = FakeSession([FakeResponse({"results": {"KE": {}}}), FakeResponse({"results": {"US": {}}})])
    service = TMDBWatchService(session=fake, cache=cache, sleep=lambda _: None)
    service.get_providers_data(3, "KE")
    service.get_providers_data(3, "US")
    assert len(fake.calls) == 2
    assert cache.ttls["tmdb-watch:providers:3:KE"] == 43200


def test_tmdb_429_retried_then_returned_as_429(client):
    _, headers = signup_and_login(client)
    from app.routes import watch_routes
    original = watch_routes.watch_service
    watch_routes.watch_service = __import__("app.services.tmdb_watch_service", fromlist=["TMDBWatchService"]).TMDBWatchService(
        session=FakeSession([FakeResponse({}, 429), FakeResponse({}, 429), FakeResponse({}, 429)]), sleep=lambda _: None
    )
    try:
        response = client.get("/api/movies/1/watch/providers", headers=headers)
    finally:
        watch_routes.watch_service = original
    assert response.status_code == 429

"""TMDB video and licensed watch-provider lookups.

Only TMDB metadata is returned. Provider URLs are deliberately never exposed;
the provider link is TMDB's own movie watch page for the requested region.
"""
import time
from threading import RLock

import requests
from flask import current_app


class TMDBWatchError(Exception):
    status_code = 502


class TMDBMovieNotFound(TMDBWatchError):
    status_code = 404


class TMDBRateLimitError(TMDBWatchError):
    status_code = 429


class TMDBUnavailableError(TMDBWatchError):
    status_code = 502


class _MemoryTTLCache:
    def __init__(self):
        self._values = {}
        self._lock = RLock()

    def get(self, key):
        with self._lock:
            entry = self._values.get(key)
            if not entry:
                return None
            expires, value = entry
            if expires <= time.monotonic():
                del self._values[key]
                return None
            return value

    def set(self, key, value, ttl):
        with self._lock:
            self._values[key] = (time.monotonic() + ttl, value)


_memory_cache = _MemoryTTLCache()


class TMDBWatchService:
    def __init__(self, session=None, cache=None, sleep=time.sleep):
        self.session = session or requests
        self.cache = cache
        self.sleep = sleep

    def _cache(self):
        if self.cache is not None:
            return self.cache
        redis_url = current_app.config.get("TMDB_REDIS_URL")
        if redis_url:
            try:
                import redis
                return redis.Redis.from_url(redis_url, decode_responses=True)
            except (ImportError, Exception):
                current_app.logger.warning("TMDB Redis cache unavailable; using memory cache")
        return _memory_cache

    @staticmethod
    def _key(parts):
        return "tmdb-watch:" + ":".join(map(str, parts))

    def _cached_get(self, key):
        try:
            value = self._cache().get(key)
            if value is None:
                return None
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            if isinstance(value, str):
                import json
                value = json.loads(value)
            return value
        except Exception:
            current_app.logger.warning("TMDB cache read failed", exc_info=True)
            return None

    def _cache_set(self, key, value, ttl):
        try:
            cache = self._cache()
            try:
                cache.set(key, value, ex=ttl)
            except TypeError:
                cache.set(key, value, ttl)
        except Exception:
            current_app.logger.warning("TMDB cache write failed", exc_info=True)

    def _get(self, path, cache_key, ttl):
        cached = self._cached_get(cache_key)
        if cached is not None:
            return cached
        headers = {}
        params = {}
        token = current_app.config.get("TMDB_ACCESS_TOKEN") or current_app.config.get("TMDB_TOKEN")
        api_key = current_app.config.get("TMDB_API_KEY")
        if not token and api_key and api_key.startswith("eyJ"):
            token = api_key
        if token:
            headers["Authorization"] = f"Bearer {token}"
        elif api_key:
            params["api_key"] = api_key
        base_url = current_app.config.get("TMDB_BASE_URL", "https://api.themoviedb.org/3").rstrip("/")
        for attempt in range(3):
            try:
                response = self.session.get(base_url + path, params=params, headers=headers, timeout=5)
            except requests.RequestException as exc:
                if attempt < 2:
                    self.sleep(0.1 * (2 ** attempt))
                    continue
                raise TMDBUnavailableError("TMDB is unavailable") from exc
            status = response.status_code
            if status == 401:
                raise TMDBUnavailableError("TMDB rejected the configured credentials")
            if status == 404:
                raise TMDBMovieNotFound("Movie not found")
            if status == 429 or status >= 500:
                if attempt < 2:
                    retry_after = response.headers.get("Retry-After")
                    try:
                        delay = min(float(retry_after), 2.0) if retry_after else 0.1 * (2 ** attempt)
                    except (TypeError, ValueError):
                        delay = 0.1 * (2 ** attempt)
                    self.sleep(delay)
                    continue
                if status == 429:
                    raise TMDBRateLimitError("TMDB rate limit exceeded")
                raise TMDBUnavailableError("TMDB is unavailable")
            if status < 200 or status >= 300:
                raise TMDBUnavailableError("Unexpected response from TMDB")
            try:
                data = response.json()
            except (ValueError, TypeError) as exc:
                raise TMDBUnavailableError("Invalid response from TMDB") from exc
            if not isinstance(data, dict):
                raise TMDBUnavailableError("Invalid response from TMDB")
            self._cache_set(cache_key, data, ttl)
            return data

    def get_watch_data(self, tmdb_id, country):
        detail = self._get(f"/movie/{tmdb_id}", self._key(("movie", tmdb_id)), 86400)
        videos_data = self._get(f"/movie/{tmdb_id}/videos", self._key(("videos", tmdb_id)), 86400)
        providers_data = self.get_providers_data(tmdb_id, country)
        videos = [v for v in videos_data.get("results", []) if v.get("site") == "YouTube" and v.get("key")]
        videos.sort(key=lambda v: ({"trailer": 0, "teaser": 1, "clip": 2}.get((v.get("type") or "").lower(), 3),
                                   not bool(v.get("official")), (v.get("name") or "").lower()))
        return {"tmdb_id": tmdb_id, "title": detail.get("title"), "videos": videos,
                "primary_trailer": self._primary_trailer(videos), "watch_providers": self._map_providers(providers_data, tmdb_id, country)}

    def get_providers_data(self, tmdb_id, country):
        return self._get(f"/movie/{tmdb_id}/watch/providers", self._key(("providers", tmdb_id, country)), 43200)

    @staticmethod
    def _primary_trailer(videos):
        if not videos:
            return {"key": None, "site": None, "name": None}
        def rank(video):
            kind = (video.get("type") or "").lower()
            official = bool(video.get("official"))
            if kind == "trailer" and official: priority = 0
            elif kind == "teaser" and official: priority = 1
            elif official: priority = 2
            elif kind == "trailer": priority = 3
            else: priority = 4
            return priority, (video.get("name") or "").lower()
        best = min(videos, key=rank)
        return {"key": best.get("key"), "site": best.get("site"), "name": best.get("name")}

    @staticmethod
    def _map_providers(data, tmdb_id, country):
        region = data.get("results", {}).get(country, {})
        link = f"https://www.themoviedb.org/movie/{tmdb_id}/watch?locale={country}"
        mapped = {"country_code": country}
        for source, target in (("flatrate", "stream"), ("rent", "rent"), ("buy", "buy")):
            mapped[target] = [{"provider_id": p.get("provider_id"), "provider_name": p.get("provider_name"),
                               "logo_path": p.get("logo_path"), "deep_link": link}
                              for p in region.get(source, [])]
        return mapped

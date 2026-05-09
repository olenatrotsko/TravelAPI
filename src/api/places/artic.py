from typing import Optional
import httpx
from core.config import settings
from core.cache import cache
from core.exceptions import ExternalAPIError, NotFoundError

IIIF_BASE = "https://www.artic.edu/iiif/2"
FIELDS = "id,title,artist_display,place_of_origin,image_id"


class ArticService:
    def __init__(self):
        self.base_url = settings.ARTIC_API_BASE
        self.ttl = settings.ARTIC_CACHE_TTL

    def _image_url(self, image_id: Optional[str]) -> Optional[str]:
        return f"{IIIF_BASE}/{image_id}/full/843,/0/default.jpg" if image_id else None

    async def fetch(self, artwork_id: int) -> dict:
        key = f"artic:{artwork_id}"
        cached = cache.get(key)
        if cached:
            return cached

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}/artworks/{artwork_id}",
                    params={"fields": FIELDS},
                )
        except httpx.RequestError as e:
            raise ExternalAPIError(f"Failed to reach Art Institute API: {e}")

        if resp.status_code == 404:
            raise NotFoundError(f"Artwork {artwork_id} not found in Art Institute of Chicago API")
        if resp.status_code != 200:
            raise ExternalAPIError(f"Art Institute API returned HTTP {resp.status_code}")

        data = resp.json().get("data", {})
        result = {
            "external_id": data["id"],
            "title": data.get("title") or "Untitled",
            "artist_display": data.get("artist_display"),
            "place_of_origin": data.get("place_of_origin"),
            "image_url": self._image_url(data.get("image_id")),
        }
        cache.set(key, result, ttl=self.ttl)
        return result

import os
import aiohttp
from typing import Optional

API_BASE = os.getenv("API_BASE_URL", "https://django-production-cc9b.up.railway.app/api/v1")


async def _get(path: str, params: dict = None) -> Optional[dict]:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE}{path}", params=params) as resp:
            if resp.status == 200:
                return await resp.json()
            return None


async def _post(path: str, data: dict) -> Optional[dict]:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_BASE}{path}", json=data) as resp:
            if resp.status in (200, 201):
                return await resp.json()
            return None


async def _patch(path: str) -> Optional[dict]:
    async with aiohttp.ClientSession() as session:
        async with session.patch(f"{API_BASE}{path}") as resp:
            if resp.status == 200:
                return await resp.json()
            return None


# ── Users ──────────────────────────────────────────────────────────────────

async def register_user(telegram_id: int, username: str = None, fullname: str = None):
    return await _post("/users/register/", {
        "telegram_id": telegram_id,
        "username": username,
        "fullname": fullname,
    })


async def get_user(telegram_id: int):
    return await _get(f"/users/{telegram_id}/")


# ── Flats ──────────────────────────────────────────────────────────────────

async def get_flats(page: int = 1, **filters) -> Optional[dict]:
    params = {"page": page, **filters}
    return await _get("/flats/", params=params)


async def get_flat(flat_id: int) -> Optional[dict]:
    return await _get(f"/flats/{flat_id}/")


async def get_profitable_flats() -> Optional[dict]:
    return await _get("/flats/profitable/")


# ── Stats ──────────────────────────────────────────────────────────────────

async def get_stats() -> Optional[dict]:
    return await _get("/stats/")


async def get_market_stats(rooms: int = None) -> Optional[dict]:
    params = {}
    if rooms:
        params["rooms"] = rooms
    return await _get("/market-stats/", params=params)
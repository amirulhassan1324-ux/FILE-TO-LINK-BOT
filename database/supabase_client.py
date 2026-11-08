"""Shared async Supabase client + small helpers used by every database module."""
import asyncio
from supabase import acreate_client, AsyncClient
from config import SUPABASE_URL, SUPABASE_KEY

_client: AsyncClient | None = None
_lock = asyncio.Lock()

PAGE_SIZE = 1000  # Supabase returns max 1000 rows per request


async def get_client() -> AsyncClient:
    """Create the client lazily (inside the running event loop) and reuse it."""
    global _client
    if _client is None:
        async with _lock:
            if _client is None:
                if not SUPABASE_URL or not SUPABASE_KEY:
                    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set")
                _client = await acreate_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


async def table(name: str):
    return (await get_client()).table(name)


async def count_rows(name: str) -> int:
    res = await (await table(name)).select("*", count="exact").limit(1).execute()
    return res.count or 0


async def fetch_all(name: str, columns: str = "*", order: str | None = None, desc: bool = False):
    """Yield every row of a table, paging past the 1000-row API limit."""
    start = 0
    while True:
        q = (await table(name)).select(columns)
        if order:
            q = q.order(order, desc=desc)
        res = await q.range(start, start + PAGE_SIZE - 1).execute()
        rows = res.data or []
        for row in rows:
            yield row
        if len(rows) < PAGE_SIZE:
            break
        start += PAGE_SIZE
      

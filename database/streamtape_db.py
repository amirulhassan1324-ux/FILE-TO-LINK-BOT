import time
from database.supabase_client import table, get_client, fetch_all

# One row per bot file (file_id = message id in BIN_CHANNEL):
#   st_id   : current Streamtape file id
#   name    : file name used on Streamtape (kept the same on every restore)
#   status  : uploading | ok | failed
#   healed  : how many times the file was restored
#   fails   : failed upload attempts in a row


def _clean(row):
    """Drop NULL columns so rec.get("last_check", 0) behaves like a missing field (as in MongoDB)."""
    return {k: v for k, v in row.items() if v is not None}


async def get(file_id):
    res = await (await table("streamtape")).select("*").eq("file_id", int(file_id)).limit(1).execute()
    rows = res.data or []
    return _clean(rows[0]) if rows else None


async def upsert(file_id, **fields):
    fields["updated"] = time.time()
    fields["file_id"] = int(file_id)
    await (await table("streamtape")).upsert(fields, on_conflict="file_id").execute()


async def inc(file_id, **counters):
    """Atomic increment (uses the `streamtape_inc` SQL function from schema.sql)."""
    client = await get_client()
    await client.rpc(
        "streamtape_inc",
        {
            "p_file_id": int(file_id),
            "p_healed": int(counters.get("healed", 0)),
            "p_fails": int(counters.get("fails", 0)),
        },
    ).execute()


async def all_records():
    return [_clean(row) async for row in fetch_all("streamtape", "*", order="file_id")]


from database.supabase_client import table


async def set_maintenance(state: bool):
    await (await table("settings")).upsert(
        {"id": "maintenance", "state": bool(state)}, on_conflict="id"
    ).execute()


async def get_maintenance():
    res = await (await table("settings")).select("state").eq("id", "maintenance").limit(1).execute()
    rows = res.data or []
    return bool(rows[0].get("state")) if rows else False
    

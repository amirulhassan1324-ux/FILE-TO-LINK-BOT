from database.supabase_client import table


async def ban_user(user_id, reason):
    await (await table("users")).upsert(
        {"id": int(user_id), "banned": True, "reason": reason}, on_conflict="id"
    ).execute()


async def unban_user(user_id):
    await (await table("users")).update({"banned": False}).eq("id", int(user_id)).execute()


async def is_user_banned(user_id):
    res = await (await table("users")).select("banned").eq("id", int(user_id)).limit(1).execute()
    rows = res.data or []
    return bool(rows[0].get("banned")) if rows else False
    

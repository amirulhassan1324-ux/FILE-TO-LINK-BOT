import time
from database.supabase_client import table, count_rows


async def save_file(file_id, file_name, file_size, mime_type, uploader_id):
    # Only the columns listed here are updated on conflict, so `links` is preserved.
    await (await table("files")).upsert(
        {
            "file_id": int(file_id),
            "file_name": file_name,
            "file_size": file_size,
            "mime_type": mime_type,
            "uploader_id": uploader_id,
            "upload_date": time.time(),
        },
        on_conflict="file_id",
    ).execute()


async def set_links(file_id, host, page_link, player_link):
    """Stores the 2 bot links of one server (page + player) on the file's record: links[host]."""
    fid = int(file_id)
    res = await (await table("files")).select("links").eq("file_id", fid).limit(1).execute()
    rows = res.data or []
    links = (rows[0].get("links") if rows else None) or {}
    links[host] = {"page": page_link, "player": player_link}
    await (await table("files")).upsert(
        {"file_id": fid, "links": links}, on_conflict="file_id"
    ).execute()


async def get_all_files(limit=300):
    res = await (
        (await table("files"))
        .select("*")
        .order("upload_date", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data or []


async def total_files_count():
    return await count_rows("files")
    

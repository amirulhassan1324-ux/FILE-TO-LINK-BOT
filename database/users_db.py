from database.supabase_client import table, count_rows, fetch_all


class Database:
    """Users table: id (bigint, telegram user id), banned, reason."""

    async def add_user(self, id):
        # ignore_duplicates -> existing rows (and their banned flag) are left untouched
        await (await table("users")).upsert({"id": int(id)}, on_conflict="id", ignore_duplicates=True).execute()

    async def total_users_count(self):
        return await count_rows("users")

    async def get_all_users(self):
        """Async iterator of user dicts. Both 'id' and '_id' keys are provided
        so old code using either keeps working."""
        async def _gen():
            async for row in fetch_all("users", "id", order="id"):
                yield {"id": row["id"], "_id": row["id"]}
        return _gen()


db = Database()

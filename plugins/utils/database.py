# Users DB for the bot plugins. Backed by Supabase (same table as database/users_db.py).
from database.users_db import db

__all__ = ["db"]

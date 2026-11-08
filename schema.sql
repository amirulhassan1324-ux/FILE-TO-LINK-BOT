-- Run this once in Supabase: Dashboard -> SQL Editor -> New query -> Run

create table if not exists public.users (
    id      bigint primary key,          -- Telegram user id
    banned  boolean not null default false,
    reason  text
);

create table if not exists public.files (
    file_id     bigint primary key,      -- message id in BIN_CHANNEL
    file_name   text,
    file_size   bigint,
    mime_type   text,
    uploader_id bigint,
    upload_date double precision,        -- unix timestamp
    links       jsonb not null default '{}'::jsonb   -- {"streamtape": {"page": "...", "player": "..."}}
);
create index if not exists files_upload_date_idx on public.files (upload_date desc);

create table if not exists public.streamtape (
    file_id     bigint primary key,
    st_id       text,
    name        text,
    status      text,                    -- uploading | ok | failed
    page_link   text,
    player_link text,
    healed      integer not null default 0,
    fails       integer not null default 0,
    last_check  double precision,
    updated     double precision
);

create table if not exists public.settings (
    id    text primary key,
    state boolean not null default false
);

-- Atomic counter increment used by database/streamtape_db.py -> inc()
create or replace function public.streamtape_inc(p_file_id bigint, p_healed integer default 0, p_fails integer default 0)
returns void
language sql
as $$
    insert into public.streamtape (file_id, healed, fails)
    values (p_file_id, p_healed, p_fails)
    on conflict (file_id) do update
    set healed = public.streamtape.healed + p_healed,
        fails  = public.streamtape.fails  + p_fails;
$$;

-- The bot uses the service_role key (server side only), which bypasses RLS.
-- Turn RLS on so the public anon key can never read these tables.
alter table public.users      enable row level security;
alter table public.files      enable row level security;
alter table public.streamtape enable row level security;
alter table public.settings   enable row level security;

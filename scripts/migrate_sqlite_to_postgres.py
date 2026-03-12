import os
import re
import sqlite3
import sys
from pathlib import Path

import psycopg2
import psycopg2.extras


def _normalize_pg_url(url: str) -> str:
    url = url.strip()
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _get_sqlite_tables(conn: sqlite3.Connection) -> list[str]:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    return [row[0] for row in cur.fetchall()]


def _get_sqlite_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    cur = conn.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cur.fetchall()]


def _get_pg_columns(cur, table: str) -> list[str]:
    cur.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema='public' AND table_name=%s",
        (table,),
    )
    return [row[0] for row in cur.fetchall()]


def _get_pg_sequences(cur, table: str) -> list[tuple[str, str]]:
    cur.execute(
        "SELECT column_name, column_default FROM information_schema.columns "
        "WHERE table_schema='public' AND table_name=%s",
        (table,),
    )
    sequences = []
    for col, default in cur.fetchall():
        if not default:
            continue
        if "nextval" not in default:
            continue
        m = re.search(r"nextval\('([^']+)'::regclass\)", default)
        if not m:
            continue
        sequences.append((col, m.group(1)))
    return sequences


def main():
    sqlite_path = os.getenv("SQLITE_PATH", "./db.sqlite3")
    pg_url = os.getenv("DATABASE_URL")
    clear_target = os.getenv("CLEAR_TARGET", "1").lower() in {"1", "true", "yes"}

    if not pg_url:
        print("DATABASE_URL is required", file=sys.stderr)
        sys.exit(1)

    sqlite_file = Path(sqlite_path)
    if not sqlite_file.exists():
        print(f"SQLite file not found: {sqlite_file}", file=sys.stderr)
        sys.exit(1)

    pg_url = _normalize_pg_url(pg_url)

    sqlite_conn = sqlite3.connect(str(sqlite_file))
    sqlite_conn.row_factory = sqlite3.Row

    pg_conn = psycopg2.connect(pg_url)
    pg_conn.autocommit = False

    try:
        pg_cur = pg_conn.cursor()
        tables = _get_sqlite_tables(sqlite_conn)

        if clear_target:
            for table in tables:
                pg_cur.execute(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE')
            pg_conn.commit()

        for table in tables:
            sqlite_cols = _get_sqlite_columns(sqlite_conn, table)
            pg_cols = _get_pg_columns(pg_cur, table)
            common = [c for c in sqlite_cols if c in pg_cols]
            if not common:
                continue

            rows = sqlite_conn.execute(
                f"SELECT {', '.join(common)} FROM {table}"
            ).fetchall()
            if not rows:
                continue

            values = [tuple(row[c] for c in common) for row in rows]
            cols_sql = ",".join([f'"{c}"' for c in common])
            insert_sql = f'INSERT INTO "{table}" ({cols_sql}) VALUES %s'
            psycopg2.extras.execute_values(pg_cur, insert_sql, values, page_size=500)
            pg_conn.commit()

            for col, seq in _get_pg_sequences(pg_cur, table):
                pg_cur.execute(f'SELECT MAX("{col}") FROM "{table}"')
                max_id = pg_cur.fetchone()[0]
                if max_id is not None:
                    pg_cur.execute("SELECT setval(%s, %s, true)", (seq, max_id))
            pg_conn.commit()

        print("Migration completed.")
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    main()

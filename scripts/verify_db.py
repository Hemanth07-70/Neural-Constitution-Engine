#!/usr/bin/env python3
"""Phase 10: Database integrity verification."""
import asyncio
import sys

import asyncpg

DB_URL = "postgresql://nce_user:nce_password@localhost:5434/nce_db"
PASS = []
FAIL = []


def check(name, condition, detail=""):
    if condition:
        PASS.append(name)
        print(f"  ✅ {name}")
    else:
        FAIL.append(name)
        print(f"  ❌ {name} — {detail}")


async def verify():
    conn = await asyncpg.connect(DB_URL)

    # 1. Required tables exist
    tables = [
        r["tablename"]
        for r in await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
    ]
    required = [
        "users",
        "organizations",
        "memberships",
        "api_keys",
        "constitutions",
        "audit_records",
        "execution_plans",
        "provider_telemetry",
        "langgraph_runs",
    ]
    for t in required:
        check(f"Table '{t}' exists", t in tables, f"Found: {tables}")

    # 2. Row counts
    for table in required:
        count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
        print(f"  ℹ️  {table}: {count} rows")

    # 3. Foreign key checks via information_schema
    fk_rows = await conn.fetch(
        """
        SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.table_name
    """
    )
    check("Foreign keys defined", len(fk_rows) > 0, "No FK constraints found")
    print(f"  ℹ️  {len(fk_rows)} foreign key constraints defined")

    # 4. Alembic version is at head
    alembic_ver = await conn.fetchval("SELECT version_num FROM alembic_version LIMIT 1")
    check("Alembic version present", alembic_ver is not None, "No alembic_version row")
    print(f"  ℹ️  Alembic head: {alembic_ver}")

    # 5. No NULL in critical columns
    null_users = await conn.fetchval("SELECT COUNT(*) FROM users WHERE email IS NULL")
    check("No NULL emails in users", null_users == 0, f"{null_users} null emails found")

    await conn.close()


print("=== Phase 10 – Database Verification ===")
asyncio.run(verify())
print(f"\n{'='*50}")
print(f"DB Verification: {len(PASS)} passed, {len(FAIL)} failed")
sys.exit(0 if not FAIL else 1)

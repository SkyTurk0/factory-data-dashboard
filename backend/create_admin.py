import os
from sqlalchemy import text
from db import engine
from werkzeug.security import generate_password_hash

ADMIN_USER = os.getenv("ADMIN_USER", "admin@example.com")
ADMIN_PASS = os.getenv("ADMIN_PASS", "Admin123!")
ADMIN_ROLE = "Admin"
ADMIN_FORCE = os.getenv("ADMIN_FORCE", "0") in ("1", "true", "True")

DEFAULT_ADMIN = "admin@example.com"

with engine.begin() as conn:
    conn.execute(text("""
        IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='Users' AND schema_id = SCHEMA_ID('dbo'))
        CREATE TABLE dbo.Users (
          Id INT IDENTITY PRIMARY KEY,
          Username NVARCHAR(200) NOT NULL UNIQUE,
          PasswordHash NVARCHAR(512) NOT NULL,
          Role NVARCHAR(20) NOT NULL
        );
    """))
    row = conn.execute(text("SELECT 1 FROM dbo.Users WHERE Username=:u"), {"u": ADMIN_USER}).fetchone()

    if ADMIN_USER != DEFAULT_ADMIN:
        conn.execute(text("DELETE FROM dbo.Users WHERE Username=:u"), {"u": DEFAULT_ADMIN})
        print(f"Removed default admin: {DEFAULT_ADMIN}")

    if not row:
        conn.execute(
            text("INSERT INTO dbo.Users (Username, PasswordHash, Role) VALUES (:u, :p, :r)"),
            {"u": ADMIN_USER, "p": generate_password_hash(ADMIN_PASS), "r": ADMIN_ROLE},
        )
        print(f"Created admin user: {ADMIN_USER} / {ADMIN_ROLE}")
    else:
        if ADMIN_FORCE:
            conn.execute(
                text("UPDATE dbo.Users SET PasswordHash=:p, Role=:r WHERE Username=:u"),
                {"u": ADMIN_USER, "p": generate_password_hash(ADMIN_PASS), "r": ADMIN_ROLE},
            )
            print(f"Updated admin user: {ADMIN_USER} / {ADMIN_ROLE}")
        else:
            print("Admin already exists (set ADMIN_FORCE=1 to update)")



import os
from sqlalchemy import text
from db import engine
from werkzeug.security import generate_password_hash

ADMIN_USER = os.getenv("ADMIN_USER", "admin@example.com")
ADMIN_PASS = os.getenv("ADMIN_PASS", "Admin123!")
ADMIN_ROLE = "Admin"

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
    if not row:
        conn.execute(
            text("INSERT INTO dbo.Users (Username, PasswordHash, Role) VALUES (:u, :p, :r)"),
            {"u": ADMIN_USER, "p": generate_password_hash(ADMIN_PASS), "r": ADMIN_ROLE},
        )
        print(f"Created admin user: {ADMIN_USER} / {ADMIN_ROLE}")
    else:
        print("Admin already exists")

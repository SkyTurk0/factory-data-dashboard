import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

# Defaults for local dev (override via env vars)
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME   = os.getenv("DB_NAME")
DB_USER   = os.getenv("DB_USER")
DB_PASS   = os.getenv("DB_PASS")

# For local dev we accept the self-signed cert inside Docker
# NOTE: Driver name must match what's installed (check ODBC Data Sources > Drivers)
ODBC_DRIVER = os.getenv("ODBC_DRIVER", "ODBC Driver 18 for SQL Server")

conn_str = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASS}@{DB_SERVER}/{DB_NAME}"
    f"?driver={ODBC_DRIVER.replace(' ', '+')}"
    f"&TrustServerCertificate=yes"
)

# pool_pre_ping helps avoid stale connections if DB restarts
engine = create_engine(conn_str, pool_pre_ping=True, future=True)

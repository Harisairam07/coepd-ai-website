import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "MSSQL_DATABASE_URL",
    "mssql+pyodbc://@localhost\\SQLEXPRESS/coepd_ai_leads?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes&Encrypt=no",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create database tables if they do not exist."""
    # Ensure model metadata is registered before create_all runs.
    import app.db_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_sqlserver_schema_compatibility()


def _ensure_sqlserver_schema_compatibility() -> None:
    """
    Backfill missing columns in existing SQL Server tables.
    This avoids runtime failures when older local schemas are reused.
    """
    insp = inspect(engine)

    if "leads" in insp.get_table_names():
        lead_columns = {col["name"].lower(): col for col in insp.get_columns("leads")}
        existing = set(lead_columns.keys())
        required = {
            "name": "NVARCHAR(255) NULL",
            "phone": "NVARCHAR(50) NULL",
            "email": "NVARCHAR(255) NULL",
            "location": "NVARCHAR(255) NULL",
            "interested_domain": "NVARCHAR(255) NULL",
            "whatsapp": "NVARCHAR(50) NULL",
            "source": "NVARCHAR(50) NULL",
            "created_at": "DATETIME2 NULL",
        }
        with engine.begin() as conn:
            for col_name, col_type in required.items():
                if col_name not in existing:
                    conn.execute(text(f"ALTER TABLE [leads] ADD [{col_name}] {col_type}"))

            # Normalize legacy text/varchar created_at to DATETIME2 when needed.
            created_at_type = str(lead_columns.get("created_at", {}).get("type", "")).lower()
            if created_at_type and ("char" in created_at_type or "text" in created_at_type):
                conn.execute(
                    text(
                        "UPDATE [leads] "
                        "SET [created_at] = COALESCE("
                        "TRY_CONVERT(datetime2, [created_at]), "
                        "CAST(TRY_CONVERT(datetimeoffset, [created_at]) AS datetime2)"
                        ") "
                        "WHERE [created_at] IS NOT NULL"
                    )
                )
                conn.execute(text("ALTER TABLE [leads] ALTER COLUMN [created_at] DATETIME2 NULL"))

    if "staff" in insp.get_table_names():
        staff_columns = {col["name"].lower(): col for col in insp.get_columns("staff")}
        existing = set(staff_columns.keys())
        required = {
            "name": "NVARCHAR(120) NOT NULL CONSTRAINT DF_staff_name DEFAULT ''",
            "email": "NVARCHAR(120) NOT NULL CONSTRAINT DF_staff_email DEFAULT ''",
            "password_hash": "NVARCHAR(255) NOT NULL CONSTRAINT DF_staff_password_hash DEFAULT ''",
            "role": "NVARCHAR(20) NOT NULL CONSTRAINT DF_staff_role DEFAULT 'staff'",
            "status": "NVARCHAR(20) NOT NULL CONSTRAINT DF_staff_status DEFAULT 'active'",
            "created_at": "DATETIME2 NULL",
        }
        with engine.begin() as conn:
            for col_name, col_type in required.items():
                if col_name not in existing:
                    conn.execute(text(f"ALTER TABLE [staff] ADD [{col_name}] {col_type}"))

            created_at_type = str(staff_columns.get("created_at", {}).get("type", "")).lower()
            if created_at_type and ("char" in created_at_type or "text" in created_at_type):
                conn.execute(
                    text(
                        "UPDATE [staff] "
                        "SET [created_at] = COALESCE("
                        "TRY_CONVERT(datetime2, [created_at]), "
                        "CAST(TRY_CONVERT(datetimeoffset, [created_at]) AS datetime2)"
                        ") "
                        "WHERE [created_at] IS NOT NULL"
                    )
                )
                conn.execute(text("ALTER TABLE [staff] ALTER COLUMN [created_at] DATETIME2 NULL"))


def db_available():
    """Return True if database connection works."""
    try:
        with engine.connect():
            return True
    except Exception:
        return False

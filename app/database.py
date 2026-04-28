import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# 🛠️ Fix for Railway/Local environment expansion issues
if "${" in DATABASE_URL:
    import re
    def expand_match(match):
        var_name = match.group(1)
        # Try both the name inside ${} and the common Railway names
        return os.getenv(var_name) or os.getenv(f"MYSQL{var_name.replace('DB_', '')}") or match.group(0)
    
    DATABASE_URL = re.sub(r'\$\{([^}]+)\}', expand_match, DATABASE_URL)

# 🏎️ Force pymysql driver (Railway default URL is often mysql://)
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

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

# ✅ ONLY PLACE get_db EXISTS
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
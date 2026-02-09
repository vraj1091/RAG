from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Try MySQL first, fallback to SQLite
DB_AVAILABLE = False
engine = None
SessionLocal = None

try:
    # Try MySQL connection
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.debug,
        connect_args={"connect_timeout": 5}  # 5 second timeout
    )
    
    # Test connection
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    logger.info("✅ MySQL database connected successfully")
    DB_AVAILABLE = True
    
except Exception as e:
    logger.warning(f"⚠️ MySQL connection failed: {e}")
    logger.info("🔄 Falling back to SQLite database...")
    
    try:
        # Fallback to SQLite
        sqlite_path = os.path.join(settings.upload_path, "rag_chatbot.db")
        os.makedirs(settings.upload_path, exist_ok=True)
        
        engine = create_engine(
            f"sqlite:///{sqlite_path}",
            connect_args={"check_same_thread": False},
            echo=settings.debug
        )
        
        # Test SQLite connection
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        
        logger.info(f"✅ SQLite database connected: {sqlite_path}")
        DB_AVAILABLE = True
        
    except Exception as sqlite_error:
        logger.error(f"❌ SQLite connection also failed: {sqlite_error}")
        logger.error("❌ Running without database - app will not work properly")
        engine = None
        DB_AVAILABLE = False

# Create session and base
if DB_AVAILABLE and engine is not None:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
else:
    SessionLocal = None
    Base = declarative_base()

def get_db():
    '''Database dependency'''
    if not DB_AVAILABLE or SessionLocal is None:
        raise Exception("Database not available")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print("✅ Database connection test succeeded.")
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")

if __name__ == "__main__":
    test_connection()

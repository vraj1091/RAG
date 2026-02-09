"""
Database initialization script for AI RAG Chatbot
Run this to set up the database schema
"""

from app.models.models import Base
from app.db.database import engine, SessionLocal
from app.core.config import settings
from sqlalchemy import text

def init_db():
    """Create all database tables"""
    print("🔄 Initializing database...")
    print(f"📍 Database: {settings.database_url}")

    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        print("🗃️ Tables created:")
        print("  - users (authentication)")
        print("  - documents (file metadata)")
        print("  - document_chunks (RAG chunks)")
        print("  - conversations (chat sessions)")
        print("  - messages (chat history)")
        print("  - vector_collections (vector store tracking)")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

def test_connection():
    """Test database connection"""
    try:
        with SessionLocal() as db:
            result = db.execute(text("SELECT 1")).fetchone()
        print(f"✅ Database connection test successful: {result}")
        return True
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AI RAG Chatbot Database Setup")
    print("=" * 40)

    if test_connection():
        init_db()
        print("🎉 Database setup complete!")
    else:
        print("❌ Cannot connect to database. Please check your configuration.")

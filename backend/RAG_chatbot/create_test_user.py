"""
Create a test user for the RAG chatbot
"""
import sys
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, DB_AVAILABLE
from app.models.models import User
from app.core.security import get_password_hash

def create_test_user():
    """Create a test user: admin/admin123"""
    
    if not DB_AVAILABLE:
        print("❌ Database not available!")
        return False
    
    db: Session = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("✅ Test user 'admin' already exists!")
            print("   Username: admin")
            print("   Password: admin123")
            return True
        
        # Create new test user
        hashed_password = get_password_hash("admin123")
        test_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hashed_password,
            is_active=True
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("✅ Test user created successfully!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@example.com")
        return True
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()

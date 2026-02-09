from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.models import User
from app.services.rag_service import get_rag_service

# FIXED: Removed leading slash - should be "api/v1/auth/token" not "/api/v1/auth/token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Decode and validate JWT token, return current user.
    Includes debug prints for troubleshooting.
    """
    print(f"🔍 Validating received token: {token[:30]}..." if len(token) > 30 else token)
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        print(f"✅ JWT payload decoded: {payload}")
        
        username: str = payload.get("sub")
        if username is None:
            print("❌ ERROR: Username missing from token payload")
            raise credentials_exception
            
        print(f"👤 Username from token: {username}")
        
    except JWTError as e:
        print(f"❌ JWT decode error: {e}")
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"❌ ERROR: User not found in database: {username}")
        raise credentials_exception
    
    if not user.is_active:
        print(f"❌ ERROR: Inactive user attempted access: {username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    print(f"✅ User authenticated successfully: {user.username} (ID: {user.id})")
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user (wrapper for backward compatibility)."""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


# NEW: RAG Service Dependency
def get_rag_service_dep(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dependency to get RAG service instance for the current user.
    Creates a new RAG service instance per request.
    """
    return get_rag_service(db, current_user.id)

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: User


class TokenData(BaseModel):
    username: Optional[str] = None


# Document schemas
class DocumentBase(BaseModel):
    filename: str
    file_type: str


class DocumentCreate(DocumentBase):
    pass


class Document(DocumentBase):
    id: int
    original_filename: str
    file_path: str
    file_size: int
    processing_status: str
    document_type: str
    user_id: int
    created_at: datetime
    extracted_text: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentStats(BaseModel):
    total_documents: int
    processed_documents: int
    file_types: Dict[str, int]
    vector_stats: Dict[str, Any]


# Chat schemas
class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    conversation_id: Optional[int] = None


class Message(MessageBase):
    id: int
    role: str
    sources: Optional[List[Dict[str, Any]]] = None
    relevance_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    title: str


class ConversationCreate(ConversationBase):
    pass


class ConversationWithMessages(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[Message] = []

    class Config:
        from_attributes = True


class Conversation(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    message: str
    conversation_id: int
    sources: Optional[List[Dict[str, Any]]] = None
    context_used: bool = False
    chunks_retrieved: int = 0
    charts: List[Dict[str, Any]] = []  # ✅ Chart data as list for multiple visualizations


# File upload schemas
class FileUploadResponse(BaseModel):
    message: str
    document: Document


class HealthResponse(BaseModel):
    status: str
    database: str
    gemini_api: str
    vector_db: str

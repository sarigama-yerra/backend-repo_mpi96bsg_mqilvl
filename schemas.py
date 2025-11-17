"""
Database Schemas for Legal AI Assistant

Each Pydantic model maps to a MongoDB collection (lowercase of class name).
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class User(BaseModel):
    name: str
    email: str
    company: Optional[str] = None
    role: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True

class Policy(BaseModel):
    title: str
    category: Literal['liability','ip','payment','indemnity','confidentiality','term','termination','general'] = 'general'
    content: str
    version: Optional[str] = None

class Document(BaseModel):
    title: str
    filename: str
    uploader_email: str
    status: Literal['uploaded','analyzing','review_ready','negotiating','finalized'] = 'uploaded'
    current_version_id: Optional[str] = None

class Clause(BaseModel):
    document_id: str
    clause_type: Literal['liability','ip','payment','indemnity','confidentiality','term','termination','other'] = 'other'
    text: str
    risk: Literal['low','medium','high','critical'] = 'medium'
    policy_refs: Optional[List[str]] = None

class Comment(BaseModel):
    document_id: str
    user_email: str
    text: str
    range_start: Optional[int] = None
    range_end: Optional[int] = None

class Message(BaseModel):
    thread_id: str
    sender_email: str
    receiver_email: str
    content: str

class Thread(BaseModel):
    document_id: Optional[str] = None
    participants: List[str]
    last_message: Optional[str] = None

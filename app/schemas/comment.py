# app/schemas/comment.py
from pydantic import BaseModel
from datetime import datetime

class CommentCreate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: int
    user_id: int
    company_id: int
    content: str
    created_at: datetime
    username: str = ""

    class Config:
        from_attributes = True
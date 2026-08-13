# app/api/comments.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentResponse
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/company/{company_id}", response_model=CommentResponse)
async def add_comment(
    company_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    new_comment = Comment(
        user_id=current_user.id,
        company_id=company_id,
        content=comment_data.content
    )
    
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    
    return CommentResponse(
        id=new_comment.id,
        user_id=new_comment.user_id,
        company_id=new_comment.company_id,
        content=new_comment.content,
        created_at=new_comment.created_at,
        username=current_user.username
    )

@router.get("/company/{company_id}", response_model=list[CommentResponse])
async def get_comments(company_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Comment, User.username)
        .join(User, Comment.user_id == User.id)
        .where(Comment.company_id == company_id)
        .order_by(desc(Comment.created_at))
        .limit(50)
    )
    
    comments = []
    for comment, username in result:
        comments.append(CommentResponse(
            id=comment.id,
            user_id=comment.user_id,
            company_id=comment.company_id,
            content=comment.content,
            created_at=comment.created_at,
            username=username
        ))
    
    return comments

@router.get("/all")
async def get_all_comments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Comment, User.username, Company.name, Company.ticker)
        .join(User, Comment.user_id == User.id)
        .join(Company, Comment.company_id == Company.id)
        .order_by(desc(Comment.created_at))
        .limit(100)
    )
    
    comments = []
    for comment, username, company_name, ticker in result:
        comments.append({
            "id": comment.id,
            "username": username,
            "company_name": company_name,
            "company_ticker": ticker,
            "company_id": comment.company_id,
            "content": comment.content,
            "created_at": str(comment.created_at)
        })
    
    return comments
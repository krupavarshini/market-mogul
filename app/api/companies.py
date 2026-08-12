# app/routers/companies.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyResponse
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.post("/create", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if company name already exists
    result = await db.execute(select(Company).where(Company.name == company_data.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Company name already taken")
    
    # Check if ticker already exists
    result = await db.execute(select(Company).where(Company.ticker == company_data.ticker))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ticker already taken")
    
    # Check if user has enough cash (costs $50,000 to start)
    if current_user.cash_balance < 50000:
        raise HTTPException(status_code=400, detail="Need $50,000 to start a company")
    
    # Deduct money from player
    current_user.cash_balance -= 50000
    
    # Create company
    new_company = Company(
        name=company_data.name,
        ticker=company_data.ticker.upper(),
        sector=company_data.sector,
        owner_id=current_user.id,
        cash=50000.0
    )
    
    db.add(new_company)
    await db.commit()
    await db.refresh(new_company)
    
    return new_company

@router.get("/my", response_model=list[CompanyResponse])
async def get_my_companies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Company).where(Company.owner_id == current_user.id)
    )
    return result.scalars().all()
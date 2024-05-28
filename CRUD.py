from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from models import Base, Account, Card, Transaction, Pincode
from database import engine, get_session

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/accounts/", response_model=Account)
async def create_account(account: Account, session: AsyncSession = Depends(get_session)):
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return account

@app.get("/accounts/", response_model=List[Account])
async def read_accounts(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Account).offset(skip).limit(limit))
    accounts = result.scalars().all()
    return accounts

@app.get("/accounts/{iban}", response_model=Account)
async def read_account(iban: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Account).where(Account.IBAN == iban))
    account = result.scalar_one_or_none()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

# Similarly, you can create endpoints for Cards, Transactions, and Pincodes

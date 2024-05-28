from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

from models import Base, Account, Card, Transaction, Pincode

# Update the DATABASE_URL with the connection details of your existing database
DATABASE_URL = "mysql+aiomysql://user:password@existing_host/existing_dbname"


# Create the SQLAlchemy engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Configure the sessionmaker
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Function to get a new session
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

app = FastAPI()

# Startup event to create tables if they don't exist (useful for new databases)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Define a Pydantic model for the withdrawal request
class WithdrawRequest(BaseModel):
    amount: int

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/api/noob/health")
async def read_health():
    return {"status": "ok"}

@app.get ("api/withdraw")
async def withdraw(amount: int):
    return {"amount": amount}

@app.get ("api/accountinfo")
async def account_info(firstname: str, lastname: str, balance: int):
    return {"firstname ": firstname, "lastname ": lastname, "balance ": balance}

@app.post("/api/withdraw/{iban}", response_model=Account)
async def withdraw(iban: str, request: WithdrawRequest, session: AsyncSession = Depends(get_session)):
    if request.amount > 200:
        raise HTTPException(status_code=400, detail="Maximum withdrawal amount is 200")
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be positive")

    result = await session.execute(select(Account).where(Account.IBAN == iban))
    account = result.scalar_one_or_none()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.balance < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    account.balance -= request.amount
    await session.commit()  # This line updates the balance in the database
    await session.refresh(account)
    return account
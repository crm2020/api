from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from datetime import datetime

from models import Base, Account, Cards, Transaction, Pincodes

# database connection settings
DATABASE_URL = f"mysql+aiomysql://root:games123@145.24.223.91/banking"

# Create the SQLAlchemy engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Configure the session maker
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


@app.get("/api/noob/health")
async def read_health():
    return {"status": "ok"}


@app.get("api/accountinfo")
async def account_info(firstname: str, lastname: str, balance: int):
    return {"firstname ": firstname, "lastname ": lastname, "balance ": balance}


@app.get("api/account/{iban}")
async def account_info(iban: str, pincode: int, uid: int, session: AsyncSession = Depends(get_session)):
    try:
        account_result = await session.execute(select(Account).where(Account.IBAN == iban))
        account = account_result.scalar_one_or_none()
        if account is None:
            raise HTTPException(status_code=404, detail="Bank does not exist")

        card_result = await session.execute(select(Cards).where(Cards.Account_IBAN == iban, Cards.CardNR == uid))
        card = card_result.scalar_one_or_none()
        if card is None:
            raise HTTPException(status_code=404, detail="Card does not exist")

        pincode_result = await session.execute(
            select(Pincodes).where(Pincodes.CardID == card.CardID, Pincodes.PinCode == pincode))
        pincode = pincode_result.scalar_one_or_none()

        if pincode is None:
            raise HTTPException(status_code=404, detail="invalid PIN")

        if card.Blocked:
            raise HTTPException(status_code=403, detail="card is blocked")

        return {"firstname": account.firstName, "lastname": account.lastName, "balance": account.balance}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"server error: {str(e)}")


@app.post("/api/withdraw/{iban}/amount:{withdrawal_amount}")
async def withdraw(iban: str, withdrawal_amount: int, request: WithdrawRequest,
                   session: AsyncSession = Depends(get_session)):
    if withdrawal_amount > 200:
        raise HTTPException(status_code=400, detail="Maximum withdrawal amount is 200")
    if withdrawal_amount <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be positive")

    try:
        account_result = await session.execute(select(Account).where(Account.IBAN == iban))
        account = account_result.scalar_one_or_none()
        if account is None:
            raise HTTPException(status_code=404, detail="Bank does not exist")

        card_result = await session.execute(
            select(Cards).where(Cards.Account_IBAN == iban, Cards.CardNR == request.uid))
        card = card_result.scalar_one_or_none()
        if card is None:
            raise HTTPException(status_code=404, detail="Card does not exist")

        pincode_result = await session.execute(
            select(Pincodes).where(Pincodes.CardID == card.CardID, Pincodes.PinCode == request.pincode))
        pincode = pincode_result.scalar_one_or_none()

        if pincode is None:
            pincode_result = await session.execute(select(Pincodes).where(Pincodes.CardID == card.CardID))
            pincode = pincode_result.scalar_one_or_none()
            if pincode is not None:
                pincode.AttemptsRemaining -= 1
                if pincode.AttemptsRemaining <= 0:
                    card.Blocked = 1
                    await session.commit()
                    raise HTTPException(status_code=403, detail="Account is blocked")
                await session.commit()
                raise HTTPException(status_code=401, detail={"attempts_remaining": pincode.AttemptsRemaining})

        if card.Blocked:
            raise HTTPException(status_code=403, detail="Account is blocked")

        if account.Balance < withdrawal_amount:
            raise HTTPException(status_code=412, detail="Insufficient balance")

        account.Balance -= withdrawal_amount

        transaction = Transaction(date=datetime.now(), amount=withdrawal_amount, account_iban=iban)
        session.add(transaction)

        await session.commit()  # This line updates the balance in the database
        await session.refresh(account)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    return {"status": "Success"}

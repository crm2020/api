from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from models import Base, Account, Card, Transaction, Pincode

DATABASE_URL = "mysql+aiomysql://root:games123@145.24.223.91/banking"

app = FastAPI()

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(     autocommit=False, autoflush=False, bind=engine, class_=AsyncSession )

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

class WithdrawRequest(BaseModel):
    uid: int
    pincode: str
    amount: int

class AccountInfoRequest(BaseModel):
    uid: int
    pincode: str

    class Config:
        orm_mode = True

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# @app.post("/users/", response_model=UserRead)
# async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
#     db_user = User(name=user.name, email=user.email)
#     db.add(db_user)
#     await db.commit()
#     await db.refresh(db_user)
#     return db_user

# @app.get("/api/accountinfo")
# async def read_users( db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Account))
#     users = result.scalars().all()
#     return users

# @app.get("/users/{user_id}", response_model=UserRead)
# async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(User).filter(User.id == user_id))
#     user = result.scalars().first()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

@app.get("/api/noob/health")
async def read_health():
    return {"status": "ok"}

@app.get("/api/account")
async def account_info(firstname: str, lastname: str, balance: int):
    return {"firstname": firstname, "lastname": lastname, "balance": balance}

@app.post("/api/accountinfo")
async def account_info(request: AccountInfoRequest, target: str = Query(...), db: AsyncSession = Depends(get_db)):
    try:
        logger.info("Processing account info request for target: %s", target)
        account_result = await db.execute(select(Account).where(Account.IBAN == target))
        account = account_result.scalar_one_or_none()
        if account is None:
            raise HTTPException(status_code=404)

        card_result = await db.execute(select(Card).where(Card.Account_IBAN == target, Card.UID == request.uid))
        card = card_result.scalar_one_or_none()
        if card is None:
            raise HTTPException(status_code=404)

        pincode_result = await db.execute(select(Pincode).where(Pincode.Cards_id == card.id, Pincode.pinCode == request.pincode))
        pincode = pincode_result.scalar_one_or_none()

        if pincode is None:
            raise HTTPException(status_code=401)

        if card.blocked:
            raise HTTPException(status_code=403)

        return {"firstname": account.firstName, "lastname": account.lastName, "balance": account.balance}
    except HTTPException as http_exc:
        logger.error("HTTPException: %s", http_exc.detail)
        raise http_exc
    except Exception as e:
        logger.error("Exception: %s", str(e))
        raise HTTPException(status_code=500)


@app.post("/api/withdraw")
async def withdraw(request: WithdrawRequest, target: str = Query(...), db: AsyncSession = Depends(get_db)):
    if request.amount > 200:
        raise HTTPException(status_code=400)
    if request.amount <= 0:
https://github.com/crm2020/api        raise HTTPException(status_code=400)

try:
    account_result = await db.execute(select(Account).where(Account.IBAN == target))
    account = account_result.scalar_one_or_none()
    if account is None:
        raise HTTPException(status_code=404)

    card_result = await db.execute(select(Card).where(Card.Account_IBAN == target, Card.UID == request.uid))
    card = card_result.scalar_one_or_none()
    if card is None:
        raise HTTPException(status_code=404)

    pincode_result = await db.execute(select(Pincode).where(Pincode.Cards_id == card.id, Pincode.pinCode == request.pincode))
    pincode = pincode_result.scalar_one_or_none()

    if pincode is None:
        pincode_result = await db.execute(select(Pincode).where(Pincode.Cards_id == card.id))
        pincode = pincode_result.scalar_one_or_none()
        if pincode is not None:
            pincode.AttemptsRemaining -= 1
            if pincode.AttemptsRemaining <= 0:
                card.Blocked = 1
                await db.commit()
                raise HTTPException(status_code=403)
            await db.commit()
            raise HTTPException(status_code=401)

    if card.Blocked:
        raise HTTPException(status_code=403)

    if account.balance < request.amount:
        raise HTTPException(status_code=412)

    account.balance -= request.amount

    transaction = Transaction(date=datetime.now(), amount=request.amount, account_iban=target)
    db.add(transaction)

    await db.commit()  # This line updates the balance in the database
    await db.refresh(account)
except HTTPException as http_exc:
    logger.error("HTTPException: %s", http_exc.detail)
    raise http_exc
except Exception as e:
    logger.error("Exception: %s", str(e))
    raise HTTPException(status_code=500)

return {"status": "Success"}
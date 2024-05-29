from sqlalchemy import Column, Date, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Account(Base):
    __tablename__ = 'account'
    IBAN = Column(String(18), primary_key=True, index=True)
    firstName = Column(String(45))
    lastName = Column(String(45))
    email = Column(String(45))
    phone = Column(String(45))
    birthDate = Column(Date)
    balance = Column(Integer)

    cards = relationship("Card", back_populates="account")
    transactions = relationship("Transaction", back_populates="account")

class Cards(Base):
    __tablename__ = 'cards'
    id = Column(Integer, primary_key=True, index=True)
    UID = Column(String(8))
    expDate = Column(Date)
    blocked = Column(Integer)
    Account_IBAN = Column(String(18), ForeignKey('account.IBAN'))

    account = relationship("Account", back_populates="cards")
    pincodes = relationship("Pincode", back_populates="card")

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    amount = Column(Integer)
    Account_IBAN = Column(String(18), ForeignKey('account.IBAN'))

    account = relationship("Account", back_populates="transactions")

class Pincodes(Base):
    __tablename__ = 'pincodes'
    pinID = Column(Integer, primary_key=True, index=True)
    pinCode = Column(Integer)
    Cards_id = Column(Integer, ForeignKey('cards.id'))
    Cards_Account_IBAN = Column(String(18), ForeignKey('account.IBAN'))

    card = relationship("Card", back_populates="pincodes")

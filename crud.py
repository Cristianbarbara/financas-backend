from sqlalchemy.orm import Session
from . import models, schemas
from .auth import get_password_hash

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: int):
    db_transaction = models.Transaction(**transaction.dict(), user_id=user_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).filter(models.Transaction.user_id == user_id).offset(skip).limit(limit).all()

def create_investment(db: Session, investment: schemas.InvestmentCreate, user_id: int):
    db_investment = models.Investment(**investment.dict(), user_id=user_id)
    db.add(db_investment)
    db.commit()
    db.refresh(db_investment)
    return db_investment

def get_investments(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Investment).filter(models.Investment.user_id == user_id).offset(skip).limit(limit).all()

def get_dashboard_data(db: Session, user_id: int):
    transactions = db.query(models.Transaction).filter(models.Transaction.user_id == user_id).all()
    investments = db.query(models.Investment).filter(models.Investment.user_id == user_id).all()
    
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    total_invested = sum(i.invested_amount for i in investments)
    total_portfolio = sum(i.current_value or i.invested_amount for i in investments)
    
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": total_income - total_expenses,
        "total_invested": total_invested,
        "total_portfolio": total_portfolio,
        "transactions": transactions[-10:],  # Last 10 transactions
        "investments": investments
    }
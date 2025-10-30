from unicodedata import category

from fastapi import APIRouter, Depends, HTTPException, status, responses
from sqlalchemy import desc
from sqlalchemy.orm import Session

from models import Transaction, Category, User
from schema import TransactionCreateResponseSchema, TransactionCreateSchema, TransactionSchema, TransactionResponse, \
    TransactionUpdateSchema
from utils import get_current_user, get_db
from utils.transaction_enums import TransactionType

transaction_router = APIRouter(prefix="/transactions", tags=['Transactions'])


@transaction_router.post("", response_model=TransactionCreateResponseSchema)
def create_transaction(transaction: TransactionCreateSchema, session: Session = Depends(get_db),
                       user_details: User = Depends(get_current_user)):
    category = session.query(Category).filter(Category.user_id == user_details.id,
                                              Category.id == transaction.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found"
        )

    new_transaction = Transaction(
        name=transaction.name,
        transaction_date=transaction.transaction_date,
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        category_id=transaction.category_id,
        user_id=user_details.id,
        description=transaction.description,
        payment_method=transaction.payment_method,
        account=transaction.account
    )

    session.add(new_transaction)
    session.commit()

    return TransactionCreateResponseSchema(
        message="Transaction has been created successfully",
        transaction=TransactionSchema.model_validate(new_transaction)
    )


@transaction_router.delete("/{transaction_id}")
def delete_transaction(transaction_id, session: Session = Depends(get_db),
                       user_details: User = Depends(get_current_user)):
    exisiting_transaction = session.query(Transaction).filter(Transaction.id == transaction_id,
                                                              Transaction.user_id == user_details.id).first()
    if not exisiting_transaction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction not found"
        )
    session.delete(exisiting_transaction)
    session.commit()

    return responses.Response(status_code=status.HTTP_204_NO_CONTENT)


@transaction_router.get("", response_model=TransactionResponse)
def list_transactions(page: int = 1, limit: int = 20, user_details=Depends(get_current_user),
                      session: Session = Depends(get_db)):
    offset = (page - 1) * limit

    transactions = session.query(Transaction).filter(Transaction.user_id == user_details.id).offset(offset).limit(limit)
    total_transaction = session.query(Transaction).filter(Transaction.user_id == user_details.id).count()
    total_pages = (total_transaction + limit - 1) // limit
    if not transactions:
        return TransactionResponse(
            page=page,
            limit=limit,
            total_transaction=total_transaction,
            total_pages=total_pages,
            message="No transactions found",
            transactions=[]
        )
    return TransactionResponse(
        page=page,
        limit=limit,
        total_transaction=total_transaction,
        total_pages=total_pages,
        message="transactions retrieved successfully",
        transactions=[TransactionSchema.model_validate(transaction) for transaction in transactions]
    )


@transaction_router.put("/{transaction_id}")
def delete_transaction(transaction_id, transactions: TransactionUpdateSchema, session: Session = Depends(get_db),
                       user_details: User = Depends(get_current_user)):
    exisiting_transaction = session.query(Transaction).filter(Transaction.id == transaction_id,
                                                              Transaction.user_id == user_details.id).first()
    if not exisiting_transaction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction not found"
        )

    if transactions.name is not None:
        exisiting_transaction.name = transactions.name
    if transactions.description is not None:
        exisiting_transaction.description = transactions.description
    if transactions.amount is not None:
        exisiting_transaction.amount = transactions.amount
    if transactions.transaction_date is not None:
        exisiting_transaction.transaction_date = transactions.transaction_date
    if transactions.transaction_type is not None:
        exisiting_transaction.transaction_type = transactions.transaction_type
    if transactions.payment_method is not None:
        exisiting_transaction.payment_method = transactions.payment_method
    if transactions.payment_method is not None:
        exisiting_transaction.payment_method = transactions.payment_method
    if transactions.account is not None:
        exisiting_transaction.account = transactions.account
    if transactions.category_id is not None:
        exisiting_transaction.category_id = transactions.category_id

    session.commit()

    return responses.Response(status_code=status.HTTP_204_NO_CONTENT)

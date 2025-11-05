from typing import Annotated, Dict, List, Optional
from langchain_core.tools import tool, InjectedToolArg
from langchain_core.runnables import RunnableConfig
from datetime import datetime
from collections import defaultdict
from sqlalchemy import func, extract

from models.transaction import Transaction, Category
from models.users import User
from utils.database import SessionLocal


def get_user_id_from_config(config: RunnableConfig) -> Optional[str]:
    """
    Helper function to extract user_id from config.
    Handles both dict and object UserDetails.
    """
    user_details = config.get("configurable", {}).get("user_details")
    if not user_details:
        return None

    # Handle both dict and object
    if isinstance(user_details, dict):
        return user_details.get("user_id")
    else:
        return getattr(user_details, "user_id", None)


@tool
def get_year_wise_category_report(
        year: int,
        config: Annotated[RunnableConfig, InjectedToolArg],
        exclude_categories: Optional[List[str]] = None
) -> Dict:
    """
    Get a year-wise category report showing monthly spending by category.

    Args:
        year: The year to generate the report for (e.g., 2024)
        exclude_categories: Optional list of category names to exclude from the report

    Returns:
        Dictionary containing monthly spending data organized by category
    """
    # Extract user_id from config
    user_details = config.get("configurable", {}).get("user_details")
    if not user_details:
        return {"error": "User context not provided"}

    # Handle both dict and object
    if isinstance(user_details, dict):
        user_id = user_details.get("user_id")
    else:
        user_id = user_details.user_id

    if not user_id:
        return {"error": "User ID not found in context"}

    session = SessionLocal()
    try:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)

        query = session.query(
            extract('month', Transaction.transaction_date).label('month'),
            Category.name.label('category_name'),
            func.sum(Transaction.amount).label('total_amount'),
            func.count(Transaction.id).label('transaction_count')
        ).join(
            Transaction.category
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).group_by(
            extract('month', Transaction.transaction_date),
            Category.id
        ).order_by(
            extract('month', Transaction.transaction_date)
        )

        if exclude_categories:
            query = query.filter(~Category.name.in_(exclude_categories))

        results = query.all()

        if not results:
            return {"message": "No transactions found for the specified year"}

        def month_name(month_num: int) -> str:
            return datetime(1900, month_num, 1).strftime("%B")

        month_data = defaultdict(list)
        for row in results:
            month_data[month_name(int(row.month))].append({
                "category": row.category_name,
                "total_amount": float(row.total_amount),
                "transaction_count": row.transaction_count,
            })

        ordered_months = sorted(
            month_data.items(),
            key=lambda x: datetime.strptime(x[0], "%B").month
        )

        response = {month: data for month, data in ordered_months}
        return {"data": response}

    finally:
        session.close()


@tool
def get_user_transactions(
        limit: int = 10,
        category_name: Optional[str] = None,
        config: Annotated[RunnableConfig, InjectedToolArg] = None
) -> Dict:
    """
    Get recent transactions for a user.

    Args:
        limit: Maximum number of transactions to return (default: 10)
        category_name: Optional category name to filter by

    Returns:
        Dictionary containing transaction data
    """
    # Extract user_id from config
    user_details = config.get("configurable", {}).get("user_details")
    if not user_details:
        return {"error": "User context not provided"}

    user_id = user_details.user_id

    session = SessionLocal()
    try:
        query = session.query(Transaction).filter(Transaction.user_id == user_id)

        if category_name:
            query = query.join(Category).filter(Category.name == category_name)

        transactions = query.order_by(
            Transaction.transaction_date.desc()
        ).limit(limit).all()

        if not transactions:
            return {"message": "No transactions found"}

        transaction_data = []
        for transaction in transactions:
            transaction_data.append({
                "id": str(transaction.id),
                "name": transaction.name,
                "amount": float(transaction.amount),
                "transaction_type": transaction.transaction_type.value,
                "transaction_date": transaction.transaction_date.isoformat(),
                "category": transaction.category.name if transaction.category else None,
                "payment_method": transaction.payment_method.value,
                "account": transaction.account.value,
                "description": transaction.description
            })

        return {"transactions": transaction_data}

    finally:
        session.close()


@tool
def get_spending_summary(
        year: int,
        month: Optional[int] = None,
        config: Annotated[RunnableConfig, InjectedToolArg] = None
) -> Dict:
    """
    Get spending summary for a user by year and optionally by month.

    Args:
        year: The year to analyze
        month: Optional month (1-12) to filter by

    Returns:
        Dictionary containing spending summary data
    """
    # Extract user_id from config
    user_details = config.get("configurable", {}).get("user_details")
    if not user_details:
        return {"error": "User context not provided"}

    user_id = user_details.user_id

    session = SessionLocal()
    try:
        start_date = datetime(year, month or 1, 1)
        if month:
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
        else:
            end_date = datetime(year + 1, 1, 1)

        income_query = session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date,
            Transaction.transaction_type == 'income'
        )

        expense_query = session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date,
            Transaction.transaction_type == 'expense'
        )

        total_income = income_query.scalar() or 0
        total_expenses = expense_query.scalar() or 0
        net_savings = float(total_income) - float(total_expenses)

        category_spending = session.query(
            Category.name,
            func.sum(Transaction.amount).label('total')
        ).join(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date,
            Transaction.transaction_type == 'expense'
        ).group_by(Category.name).order_by(
            func.sum(Transaction.amount).desc()
        ).limit(5).all()

        top_categories = [
            {"category": cat.name, "amount": float(cat.total)}
            for cat in category_spending
        ]

        return {
            "period": f"{year}" + (f"-{month:02d}" if month else ""),
            "total_income": float(total_income),
            "total_expenses": float(total_expenses),
            "net_savings": net_savings,
            "top_spending_categories": top_categories
        }

    finally:
        session.close()


@tool
def get_categories(
        config: Annotated[RunnableConfig, InjectedToolArg]
) -> Dict:
    """
    Get all categories for a user.

    Returns:
        Dictionary containing category data
    """
    # Extract user_id from config
    user_details = config.get("configurable", {}).get("user_details")
    if not user_details:
        return {"error": "User context not provided"}

    user_id = user_details.user_id

    session = SessionLocal()
    try:
        categories = session.query(Category).filter(
            Category.user_id == user_id,
            Category.is_active == True
        ).all()

        if not categories:
            return {"message": "No categories found"}

        category_data = []
        for category in categories:
            category_data.append({
                "id": str(category.id),
                "name": category.name,
                "description": category.description,
                "is_active": category.is_active
            })

        return {"categories": category_data}

    finally:
        session.close()


@tool
def create_category(
        category_name: str,
        category_description: str,
        config: Annotated[RunnableConfig, InjectedToolArg] = None
) -> Dict:
    """
    Create a new category for a user.

    Args:
        category_name: The name of the new category.
        category_description: A brief description of the category.

    Returns:
        dict: A dictionary containing the created category's data
    """
    # Extract user_id from config
    user_details = config.get("configurable", {}).get("user_details")
    if not user_details:
        return {"error": "User context not provided"}

    user_id = user_details.user_id

    session = SessionLocal()
    try:
        existing_category = session.query(Category).filter(
            Category.user_id == user_id,
            Category.name == category_name
        ).first()

        if existing_category:
            return {
                "message": "Category already present",
                "category": {
                    "id": str(existing_category.id),
                    "name": existing_category.name,
                    "description": existing_category.description
                }
            }

        new_category = Category(
            name=category_name,
            description=category_description,
            user_id=user_id
        )
        session.add(new_category)
        session.commit()

        return {
            "message": "Category successfully created",
            "category": {
                "id": str(new_category.id),
                "name": new_category.name,
                "description": new_category.description
            }
        }
    finally:
        session.close()
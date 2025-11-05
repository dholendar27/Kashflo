from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from starlette import status
from starlette.responses import JSONResponse

from utils import get_db, get_current_user
from models import User, Transaction, Category
from schema import YearWiseCategoryReportSchema

report_router = APIRouter(prefix="/report", tags=['reports'])


@report_router.get("/category/year")
def YearWiseCategoryReport(filter_data: YearWiseCategoryReportSchema, session: Session = Depends(get_db),
                           user: User = Depends(get_current_user)):
    start_date = datetime(filter_data.year, 1, 1)
    end_date = datetime(filter_data.year, 12, 31, 23, 59, 59)

    query = session.query(
        extract('month', Transaction.transaction_date).label('month'),
        Category.name.label('category_name'),
        func.sum(Transaction.amount).label('total_amount'),
        func.count(Transaction.id).label('transaction_count')
    ).join(
        Transaction.category
    ).filter(
        Transaction.user_id == user.id,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).group_by(extract('month', Transaction.transaction_date), Category.id).order_by(
        extract('month', Transaction.transaction_date))

    if filter_data.exclude:
        query = query.filter(~Category.name.in_(filter_data.exclude))

    # Execute query
    results = query.all()

    if not results:
        return JSONResponse({"message": "No Transactions found"}, status_code=status.HTTP_400_BAD_REQUEST)

    # Convert month number → month name
    def month_name(month_num: int) -> str:
        return datetime(1900, month_num, 1).strftime("%B")

    # Group results by month
    month_data = defaultdict(list)
    for row in results:
        month_data[month_name(int(row.month))].append({
            "category": row.category_name,
            "total_amount": float(row.total_amount),
            "transaction_count": row.transaction_count,
        })

    # Sort months in natural order (Jan → Dec)
    ordered_months = sorted(
        month_data.items(),
        key=lambda x: datetime.strptime(x[0], "%B").month
    )

    # Convert to dict for JSON response
    response = {month: data for month, data in ordered_months}

    return JSONResponse({"message": "Transaction retrieved successfull", "data": response},
                        status_code=status.HTTP_200_OK)

from fastapi import FastAPI
import uvicorn

from routes import user_router, categories_router, transaction_router, report_router, agents_router

from models import User, BlackListToken, Category, Transaction
from utils import engine, Base

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(user_router)
app.include_router(categories_router)
app.include_router(transaction_router)
app.include_router(report_router)
app.include_router(agents_router)

if __name__ == "__main__":
    uvicorn.run(app, port=8000)

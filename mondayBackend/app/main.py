from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base_class import Base
from app.db.session import engine

from app.api.v1.api import api_router


app = FastAPI()
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)

app.include_router(api_router, prefix="/api/v1")

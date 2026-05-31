import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi_app.api.v1.router import api_router

app = FastAPI(
    title="Social API",
    version="1.0.0",
)

cors_origins = os.getenv("CORS_ORIGINS", "*")
allow_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def health_check():
    return {"message": "FastAPI Social API is running"}

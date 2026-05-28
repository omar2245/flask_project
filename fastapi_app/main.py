from fastapi import FastAPI

from fastapi_app.api.v1.router import api_router

app = FastAPI(
    title="Social API",
    version="1.0.0",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def health_check():
    return {"message": "FastAPI Social API is running"}

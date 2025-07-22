from fastapi import FastAPI
from .database import init_db
from .routers import router

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
def startup():
    init_db()

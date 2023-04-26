from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import main, hue

app = FastAPI(
    title="Home API",
    description="API for controlling my home",
    version="0.1.0"
)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(main.router, prefix="/api")
app.include_router(hue.router, prefix="/api/hue")

from fastapi import FastAPI

from .routers import main, hue

app = FastAPI()


app.include_router(main.router)
app.include_router(hue.router)

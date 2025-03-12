from fastapi import FastAPI, HTTPException, Request

from .database import Base, get_engine
from .routers import car_parser

app = FastAPI()

app.include_router(car_parser.router)

@app.on_event("startup")
def startup():
    print("started up")
    print(Base.metadata.tables)
    Base.metadata.create_all(bind=get_engine())
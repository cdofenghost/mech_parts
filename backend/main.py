from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
import uvicorn

from .database import Base, init_db, engine
from .routers import car_parser
from .routers.cart import cart_router
from .models.order import Order
from .auth.routes import auth_router

app = FastAPI()

app.include_router(car_parser.router)
app.include_router(cart_router)
app.include_router(auth_router)
Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def startup():
    print("started up")
    print(Base.metadata.tables)
    init_db()

@app.get("/")
def test():
    return FileResponse("C:/Users/Konstantin Denisov/AppData/Local/Programs/Python/Python311/hackathon/mech_parts/frontend-extensions/search.html")    

# if __name__ == '__main__':
#     uvicorn.run(app, port=8080, host='192.168.17.77')
import asyncio
from datetime import datetime, time

from fastapi import FastAPI, Depends, HTTPException, Cookie
from fastapi_users import FastAPIUsers
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

from auth import auth_backend
from manager import get_user_manager
from mqtt_client import MqttClient
from typing import Annotated
from fastapi.responses import JSONResponse

import crud
import models
import schemas
from database import SessionLocal, engine, User
from schemas import UserCreate, UserRead

models.Base.metadata.create_all(bind=engine)


app = FastAPI()

mc = MqttClient()

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)


app.include_router(
    fastapi_users.get_register_router(UserCreate, UserRead),
    prefix="/auth",
    tags=["auth"],
)


# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:63342"],
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы
    allow_headers=["*"],  # Разрешить все заголовки
)

# Храним полученные данные
illumination_data = None
temperature_data = None
value_data = None

# Асинхронное ожидание данных
illumination_data_event = asyncio.Event()
temperature_data_event = asyncio.Event()
value_data_event = asyncio.Event()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email alredy registered")
    return crud.create_user(db=db, user=user)


@app.get("/users")
def read_users(skip: int = 0,
               limit: int = 100,
               db: Session = Depends(get_db),
               ads_id: Annotated[str | None, Cookie()] = None,
               ):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users, {"ads_id": ads_id}


@app.get("/users/{user_email}")
def read_user(user_email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_email=user_email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/devices/")
def create_device_for_user(
        user_id: int, device: schemas.DeviceCreate, db: Session = Depends(get_db)
):
    return crud.create_user_device(db=db, device=device, user_id=user_id)


@app.get("/devices/{device_id}")
def read_device(device_id: int, db: Session = Depends(get_db)):
    db_device =crud.get_device(db, device_id=device_id)
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device


@app.get("/devices/{device_secret_key}")
def read_device(device_secret_key: str, db: Session = Depends(get_db)):
    db_device =crud.get_device(db, device_id=device_secret_key)
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device


@app.post("/calibrate")
async def calibrate():
    mc.send_topic("home/calibrate")


@app.post("/close")
async def close(close_by_time: time):
    mc.send_topic("home/close")
    return {"close_by_time": close_by_time}


@app.post("/open")
async def open(open_by_time: time):
    mc.send_topic("home/open")
    return {"open_by_time": open_by_time}


@app.post("/control_illumination")
async def control_illumination(control_illumination_data: int):
    mc.send_topic("home/control_illumination")
    return {"control_illumination_data": control_illumination_data}


@app.post("/control_temperature")
async def control_temperature(control_temperature_data: int):
    mc.send_topic("home/control_temperature")
    return {"control_temperature_data": control_temperature_data}


@app.post("/value")
async def value(value_data: int):
    mc.send_topic("home/value")
    return {"value_data": value_data}


@app.get("/control_illumination")
async def control_illumination(secret_key: str):
    global illumination_data
    await illumination_data_event.wait()    # Ожидание получения данных
    illumination_data_event.clear()      # Сброс для ожидания следующих данных
    return JSONResponse(content=control_illumination)


@app.get("/control_temperature")
async def control_temperature():
    global temperature_data
    await temperature_data_event.wait()  # Ожидание получения данных
    temperature_data_event.clear()  # Сброс для ожидания следующих данных
    return JSONResponse(content=control_temperature)


@app.get("/value")
async def value():
    global value_data
    await value_data_event.wait()  # Ожидание получения данных
    value_data_event.clear()  # Сброс для ожидания следующих данных
    return JSONResponse(content=value)
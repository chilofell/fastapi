import asyncio
from fastapi import FastAPI, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from mqtt_client import MqttClient
from typing import Annotated
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import crud
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

mc = MqttClient()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://5.23.53.69/token")


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
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email alredy registered")
    return crud.create_user(db=db, user=user)


@app.get("/users")
def read_users(skip: int = 0,
               limit: int = 100,
               db: Session = Depends(get_db),
               ads_id: Annotated[str | None, Cookie()] = None,
               token: Annotated[str, Depends(oauth2_scheme)]):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users, {"ads_id": ads_id, "token": token}


@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/devices/")
def create_device_for_user(
        user_id: int, device: schemas.DeviceCreate, db: Session = Depends(get_db)
):
    return crud.create_user_device(db=db, device=device, user_id=user_id)


@app.get("/devices")
def read_devices(skip: int = 0, limit: int = 0, db: Session = Depends(get_db)):
    devices = crud.get_devices(db, skip=skip, limit=limit)
    return devices


@app.post("/calibrate")
async def calibrate():
    mc.send_topic("home/calibrate")


@app.post("/close")
async def close():
    mc.send_topic("home/close")


@app.post("/open")
async def open():
    mc.send_topic("home/open")


@app.post("/control_illumination")
async def control_illumination():
    mc.send_topic("home/control_illumination")


@app.post("/control_temperature")
async def control_temperature():
    mc.send_topic("home/control_temperature")


@app.post("/value")
async def value():
    mc.send_topic("home/value")


@app.get("/control_illumination")
async def control_illumination():
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
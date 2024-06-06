import asyncio
from datetime import time

from fastapi import FastAPI, Cookie
from rich import status
from mqtt_client import MqttClient
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

import models
import schemas
import crud
from database import engine
from security import *
from dependencies import get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

mc = MqttClient()

# Храним полученные данные
illumination_data = None
temperature_data = None
value_data = None

# Асинхронное ожидание данных
illumination_data_event = asyncio.Event()
temperature_data_event = asyncio.Event()
value_data_event = asyncio.Event()


@app.post("/users")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    user.password = hashed_password

    return crud.create_user(db=db, user=user)


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> schemas.Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")


@app.get("/users/user/", response_model=schemas.User)
async def read_users_user(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
):
    return current_user


@app.get("/users/user/devices/")
async def read_own_devices(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
):
    return [{"device_id": "Foo", "owner": current_user.username}]


@app.get("/users")
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    ads_id: Annotated[str | None, Cookie()] = None,
    current_user: schemas.TokenData = Depends(get_current_user)
):
    users = crud.get_users(db, skip=skip, limit=limit)
    for user in users:
        user.ads_id = ads_id
    return users




@app.get("/users/{user_email}")
def read_user(user_email: str, user_password: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, email=user_email, password=user_password)
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
    db_device =crud.get_device(db, device_secret_key=device_secret_key)
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


@app.delete("/devices/{device_secret_key}")
async def delete_device(device_secret_key: str):
    with Session(engine) as session:
        device = session.get(schemas.Device, device_secret_key)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        session.delete(device)
        session.commit()
        return {"Ok": True}

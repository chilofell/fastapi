from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from mqtt_client import MqttClient

import crud
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

mc = MqttClient()


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
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


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


@app.post("/сopcontrol_illuminationen")
async def сopcontrol_illuminationen():
    mc.send_topic("home/сopcontrol_illuminationen")


@app.post("/control_temperature")
async def control_temperature():
    mc.send_topic("home/control_temperature")

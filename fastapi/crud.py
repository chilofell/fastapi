from sqlalchemy.orm import Session
from security import verify_password, get_password_hash

import models
import schemas


# Чтение данных одного пользователя по имени пользователя
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user(db: Session, email: str, password: str):
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if db_user and verify_password(password, db_user.hashed_password):
        return db_user
    return None


# Чтение нескольких пользователей
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, email=user.email, hashed_password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Чтение данных одного устройства по id
def get_device(db: Session, device_id: int):
    return db.query(models.Device).filter(models.Device.id == device_id).first()


# Чтение данных одного устройства по secret_key
def get_device(db: Session, device_secret_key: str):
    return db.query(models.Device).filter(models.Device.secret_key == device_secret_key).first()


# Чтение устройств
def get_devices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Device).offset(skip).limit(limit).all()


def create_user_device(db: Session, device: schemas.DeviceCreate, user_id: int):
    db_device = models.Device(**device.dict(), owner_id=user_id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

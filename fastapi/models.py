from sqlalchemy import Column, ForeignKey, Integer, String, Time
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    password = Column(String)

    devices = relationship("Device", back_populates="owner")


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    secret_key = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    illumination = Column(Integer)
    temperature = Column(Integer)
    close_by_time = Column(Time)
    open_by_time = Column(Time)
    scale_value = Column(Integer)

    owner = relationship("User", back_populates="devices")

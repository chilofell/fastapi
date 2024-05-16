from pydantic import BaseModel

class DeviceBase(BaseModel):
    name: str


class DeviceCreate(DeviceBase):
    pass


class Device(DeviceBase):
    id: int
    owner_id: int
    secret_key: str
    illumination: int
    temperature: int
    close_by_time: str
    open_by_time: str
    value: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    name: str

    class Config:
        orm_mode = True
from pydantic import BaseModel


class DeviceBase(BaseModel):
    name: str
    secret_key: str


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
    scale_value: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(UserBase):
    id: int
    city: str | None = None

    class Config:
        orm_mode = True


class UserInDB(User):
    hashed_password: str

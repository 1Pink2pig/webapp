from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Any
import datetime

# --- User 部分 ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    realName: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    intro: Optional[str] = None
    user_type: Optional[str] = None
    register_time: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True

# --- Need (需求) 交互模型 ---
class NeedCreate(BaseModel):
    serviceType: str
    title: str
    description: Optional[str]
    imgUrls: Optional[List[str]] = None
    videoUrl: Optional[str] = None
    region: Optional[str] = None

class NeedOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    region: Optional[str]
    serviceType: str
    imgUrls: Optional[List[str]] = None
    videoUrl: Optional[str] = None
    status: int
    hasResponse: Optional[bool] = False
    hasAccepted: Optional[bool] = False
    userId: int = 0
    userName: Optional[str] = None
    createTime: Optional[datetime.datetime] = None

    @validator('imgUrls', pre=True, always=True)
    def ensure_img_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return v.split(',') if v else []
        return v

    @validator('userId', pre=True, always=True)
    def map_user_id(cls, v, values):
        if v:
            return v
        # try typical ORM attribute name
        return values.get('user_id') or 0

    class Config:
        orm_mode = True

# --- Service (服务/响应) 交互模型 ---
class ServiceCreate(BaseModel):
    needId: Optional[int] = None
    needTitle: Optional[str] = None
    serviceType: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    files: Optional[List[Any]] = None

class ServiceOut(BaseModel):
    id: int
    need_id: Optional[int] = None
    title: Optional[str]
    service_type: Optional[str]
    content: Optional[str]
    status: int
    user_id: int
    create_time: Optional[datetime.datetime]

    class Config:
        orm_mode = True

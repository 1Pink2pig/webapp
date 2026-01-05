from pydantic import BaseModel, EmailStr, field_validator
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
    id: int          # ✅ 修正：改成 id，匹配数据库
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    intro: Optional[str] = None
    user_type: Optional[str] = None
    create_time: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True  # ✅ 修正：新版写法

# --- Need (需求) 交互模型 ---
class NeedCreate(BaseModel):
    serviceType: str
    title: str
    description: str
    imgUrls: Optional[List[str]] = []
    videoUrl: Optional[str] = None
    region: Optional[str] = None

class NeedOut(BaseModel):
    id: int          # ✅ 修正：数据库叫 id，这里必须叫 id
    title: str
    description: Optional[str]
    region: Optional[str]
    serviceType: str
    imgUrls: Optional[List[str]] = []
    videoUrl: Optional[str]
    status: str      # ✅ 修正：数据库通常是字符串类型
    userId: int = 0  # 这里的 userId 是为了给前端用的，下面用 validator 映射
    user_id: int     # 数据库里的真实字段
    create_time: Optional[datetime.datetime]

    # ✅ 关键修正：把数据库里的逗号分隔字符串，转回成数组给前端
    @field_validator('imgUrls', mode='before')
    def parse_img_urls(cls, v):
        if isinstance(v, str) and v:
            return v.split(',')
        if v is None:
            return []
        return v

    # ✅ 关键修正：把 id 映射给 userId (兼容前端习惯)
    @field_validator('userId', mode='before')
    def map_user_id(cls, v, info):
        # 尝试从对象中获取 user_id
        return info.data.get('user_id', 0)

    class Config:
        from_attributes = True

# --- Service (服务/响应) 交互模型 ---
class ServiceCreate(BaseModel):
    needId: int
    needTitle: Optional[str] = None
    serviceType: Optional[str] = None
    title: str
    content: str
    files: Optional[List[Any]] = []

class ServiceOut(BaseModel):
    id: int          # ✅ 修正：改成 id
    need_id: int     # 数据库字段
    title: Optional[str]
    service_type: Optional[str]
    content: Optional[str]
    status: int
    user_id: int
    create_time: Optional[datetime.datetime]

    class Config:
        from_attributes = True
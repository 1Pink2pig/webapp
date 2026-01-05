from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from .database import Base
import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=True)
    hashed_password = Column(String(256), nullable=False)
    full_name = Column(String(128), nullable=True)
    phone = Column(String(32), nullable=True)
    intro = Column(Text, nullable=True)
    user_type = Column(String(64), nullable=True, default="普通用户")
    register_time = Column(DateTime, default=datetime.datetime.utcnow)
    update_time = Column(DateTime, default=datetime.datetime.utcnow)

    needs = relationship("Need", back_populates="owner")
    services = relationship("Service", back_populates="owner")


class Need(Base):
    __tablename__ = "needs"
    id = Column(Integer, primary_key=True, index=True)

    # --- 严格对应 NeedForm.vue ---
    title = Column(String(200), nullable=False)  # 需求主题
    description = Column(Text, nullable=True)  # 需求描述
    region = Column(String(100), nullable=True)  # 地域
    service_type = Column(String(100), nullable=False)  # 服务类型 (前端 serviceType)

    # --- 文件字段 (前端传数组，后端存 JSON) ---
    img_urls = Column(JSON, nullable=True)  # 图片链接列表 (前端 imgUrls)
    video_url = Column(String(500), nullable=True)  # 视频链接 (前端 videoUrl)

    status = Column(Integer, default=0)  # 0:已发布, -1:已取消

    owner_id = Column(Integer, ForeignKey("users.id"))
    create_time = Column(DateTime, default=datetime.datetime.utcnow)
    update_time = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="needs")
    responses = relationship("Service", back_populates="need")


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)

    # --- 严格对应 ServiceForm.vue ---
    title = Column(String(200), nullable=True)  # 服务自荐主题
    content = Column(Text, nullable=True)  # 自荐描述 (前端传 content)
    service_type = Column(String(100), nullable=True)  # 服务类型
    files = Column(JSON, nullable=True)  # 文件列表 JSON (前端 files)

    status = Column(Integer, default=0)  # 0:待接受, 1:已接受, 2:已拒绝

    need_id = Column(Integer, ForeignKey("needs.id"))  # 关联的需求
    owner_id = Column(Integer, ForeignKey("users.id"))  # 响应者

    create_time = Column(DateTime, default=datetime.datetime.utcnow)
    update_time = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="services")
    need = relationship("Need", back_populates="responses")
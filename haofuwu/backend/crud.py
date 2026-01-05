from sqlalchemy.orm import Session
from . import models, schemas, utils
import datetime
# 确保导入了 verify_password
from .utils import verify_password


# ==========================================
# 用户 (User) 相关逻辑
# ==========================================

def create_user(db: Session, user_in: schemas.UserCreate):
    hashed = utils.get_password_hash(user_in.password)
    now = datetime.datetime.utcnow()
    full_name = user_in.realName if getattr(user_in, 'realName', None) else user_in.full_name
    db_user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed,
        full_name=full_name,
        phone=user_in.phone,
        user_type="普通用户",
        register_time=now,
        update_time=now
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# ==========================================
# 需求 (Need) 相关逻辑
# ==========================================

def create_need(db: Session, user_id: int, need_in: schemas.NeedCreate):
    import datetime
    # 前端会传 imgUrls 作为数组，直接存入 JSON 列
    img_list = need_in.imgUrls if need_in.imgUrls else []

    db_need = models.Need(
        owner_id=user_id,
        title=need_in.title,
        service_type=need_in.serviceType,
        region=need_in.region,
        description=need_in.description,
        img_urls=img_list,
        video_url=need_in.videoUrl,
        status=0,  # 0=发布中
        create_time=datetime.datetime.now(),
        update_time=datetime.datetime.now()
    )
    db.add(db_need)
    db.commit()
    db.refresh(db_need)
    return db_need


def get_need(db: Session, need_id: int):
    return db.query(models.Need).filter(models.Need.id == need_id).first()


def get_needs(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Need).order_by(models.Need.create_time.desc()).offset(skip).limit(limit).all()


def get_needs_my_list(db: Session, user_id: int, keyword: str = None, service_type: str = None):
    # 查询当前用户发布的需求
    query = db.query(models.Need).filter(models.Need.owner_id == user_id)
    if keyword:
        query = query.filter(models.Need.title.contains(keyword))
    if service_type:
        query = query.filter(models.Need.service_type == service_type)

    needs = query.order_by(models.Need.create_time.desc()).all()

    # 转换为 Schema 格式返回
    results = []
    for n in needs:
        # img_urls 字段现在已经是列表或 None
        img_list = n.img_urls if n.img_urls else []

        # 简单判断是否有响应
        has_resp = False
        if hasattr(n, 'responses') and n.responses:
            has_resp = len(n.responses) > 0

        # 构造 NeedOut 对象
        results.append(schemas.NeedOut(
            id=n.id,
            title=n.title,
            description=n.description,
            region=n.region,
            serviceType=n.service_type,
            imgUrls=img_list,
            videoUrl=n.video_url,
            status=int(n.status) if n.status is not None else 0,
            hasResponse=has_resp,
            userId=n.owner_id,
            createTime=n.create_time
        ))
    return results


def update_need(db: Session, need_id: int, need_in: schemas.NeedCreate):
    import datetime
    db_need = get_need(db, need_id)
    if db_need:
        db_need.title = need_in.title
        db_need.service_type = need_in.serviceType
        db_need.region = need_in.region
        db_need.description = need_in.description
        # 直接保存列表
        db_need.img_urls = need_in.imgUrls if need_in.imgUrls else []
        db_need.video_url = need_in.videoUrl
        db_need.update_time = datetime.datetime.now()
        db.commit()
        db.refresh(db_need)
    return db_need


def cancel_need(db: Session, need_id: int):
    db_need = get_need(db, need_id)
    if db_need:
        db_need.status = 2  # 2=已取消
        db.commit()
    return db_need


def delete_need(db: Session, need_id: int):
    db_need = get_need(db, need_id)
    if db_need:
        db.delete(db_need)
        db.commit()
    return True


# ==========================================
# 服务 (Service) 相关逻辑
# ==========================================

def create_service(db: Session, owner_id: int, svc_in: schemas.ServiceCreate):
    # files 使用 JSON 存储（前端会传数组对象）
    files_val = svc_in.files if svc_in.files else []

    db_svc = models.Service(
        title=svc_in.title,
        content=svc_in.content,
        service_type=svc_in.serviceType,
        files=files_val,
        need_id=svc_in.needId,
        owner_id=owner_id,
        status=0
    )
    db.add(db_svc)
    db.commit()
    db.refresh(db_svc)
    return db_svc


def get_service_list(db: Session, keyword: str = None, service_type: str = None):
    query = db.query(models.Service)
    if keyword:
        query = query.filter(models.Service.title.contains(keyword))
    if service_type:
        query = query.filter(models.Service.service_type == service_type)

    services = query.order_by(models.Service.create_time.desc()).all()

    results = []
    for s in services:
        results.append(schemas.ServiceOut(
            id=s.id,
            need_id=s.need_id,
            title=s.title,
            service_type=s.service_type,
            content=s.content,
            status=int(s.status) if s.status is not None else 0,
            user_id=s.owner_id,
            create_time=s.create_time
        ))
    return results


def get_service(db: Session, service_id: int):
    return db.query(models.Service).filter(models.Service.id == service_id).first()


def get_my_service_list(db: Session, user_id: int):
    # 1. 查数据库：找 owner_id 是我的服务
    services = db.query(models.Service).filter(models.Service.owner_id == user_id).order_by(
        models.Service.create_time.desc()).all()

    # 2. 转换成 Schema 格式 (ServiceOut)
    results = []
    for s in services:
        results.append(schemas.ServiceOut(
            id=s.id,
            need_id=s.need_id,
            title=s.title,
            service_type=s.service_type,
            content=s.content,
            status=int(s.status) if s.status is not None else 0,
            user_id=s.owner_id,
            create_time=s.create_time
        ))
    return results


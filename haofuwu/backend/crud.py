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
    # 返回序列化后的 NeedOut 列表，避免 FastAPI 的 response_model 校验失败
    query = db.query(models.Need).order_by(models.Need.create_time.desc()).offset(skip).limit(limit)
    needs = query.all()

    results = []
    for n in needs:
        img_list = n.img_urls if getattr(n, 'img_urls', None) else []
        has_resp = False
        if hasattr(n, 'responses') and n.responses:
            has_resp = len(n.responses) > 0
        # get username from relationship if available
        username = None
        try:
            username = n.owner.username if getattr(n, 'owner', None) else None
        except Exception:
            username = None
        # fallback: try fetching user from DB if owner relationship not available
        if not username and getattr(n, 'owner_id', None):
            try:
                user = get_user_by_id(db, n.owner_id)
                username = user.username if user else None
            except Exception:
                username = None
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
            userName=username,
            createTime=n.create_time
        ))
    return results


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

        # publisher username
        username = None
        try:
            username = n.owner.username if getattr(n, 'owner', None) else None
        except Exception:
            username = None
        # fallback: try fetching user from DB if owner relationship not available
        if not username and getattr(n, 'owner_id', None):
            try:
                user = get_user_by_id(db, n.owner_id)
                username = user.username if user else None
            except Exception:
                username = None

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
            userName=username,
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


def update_service(db: Session, service_id: int, owner_id: int, svc_in: schemas.ServiceCreate):
    """Update a service record. Only the owner may update their service.
    Fields provided in svc_in will overwrite existing values.
    """
    db_svc = get_service(db, service_id)
    if not db_svc:
        return None
    if db_svc.owner_id != owner_id:
        # caller should check permissions and return appropriate response
        return False

    # Update only provided fields
    if getattr(svc_in, 'title', None) is not None:
        db_svc.title = svc_in.title
    if getattr(svc_in, 'content', None) is not None:
        db_svc.content = svc_in.content
    if getattr(svc_in, 'serviceType', None) is not None:
        db_svc.service_type = svc_in.serviceType
    if getattr(svc_in, 'files', None) is not None:
        db_svc.files = svc_in.files
    if getattr(svc_in, 'needId', None) is not None:
        db_svc.need_id = svc_in.needId

    db.commit()
    db.refresh(db_svc)
    return db_svc


def get_services_by_need(db: Session, need_id: int):
    """Return a list of service dicts for a given need id, including publisher username."""
    query = db.query(models.Service).filter(models.Service.need_id == need_id)
    services = query.order_by(models.Service.create_time.desc()).all()
    results = []
    for s in services:
        username = None
        try:
            username = s.owner.username if getattr(s, 'owner', None) else None
        except Exception:
            username = None
        if not username and getattr(s, 'owner_id', None):
            try:
                user = get_user_by_id(db, s.owner_id)
                username = user.username if user else None
            except Exception:
                username = None
        results.append({
            'id': s.id,
            'serviceId': s.id,
            'needId': s.need_id,
            'serviceType': s.service_type,
            'title': s.title,
            'content': s.content,
            'status': int(s.status) if s.status is not None else 0,
            'userId': s.owner_id,
            'userName': username or '',
            'createTime': s.create_time
        })
    return results


def accept_service(db: Session, service_id: int, need_owner_id: int):
    """Accept a service response. Only the owner of the related need may accept.
    When accepting, mark the chosen service as status=1 and mark other services for the same need as status=2.
    Returns True on success, False on permission error, None if service not found.
    """
    svc = get_service(db, service_id)
    if not svc:
        return None
    # ensure current user owns the need
    if not svc.need_id:
        return False
    need = get_need(db, svc.need_id)
    if not need or need.owner_id != need_owner_id:
        return False

    # set chosen service to accepted
    svc.status = 1
    # set other services for the same need to rejected
    others = db.query(models.Service).filter(models.Service.need_id == svc.need_id, models.Service.id != svc.id).all()
    for o in others:
        o.status = 2
    db.commit()
    db.refresh(svc)
    return True


def reject_service(db: Session, service_id: int, need_owner_id: int):
    """Reject a service response. Only the owner of the related need may reject.
    Returns True on success, False on permission error, None if service not found.
    """
    svc = get_service(db, service_id)
    if not svc:
        return None
    if not svc.need_id:
        return False
    need = get_need(db, svc.need_id)
    if not need or need.owner_id != need_owner_id:
        return False

    svc.status = 2
    db.commit()
    db.refresh(svc)
    return True

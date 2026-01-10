from fastapi import APIRouter, Depends, HTTPException, Query, Request
import logging
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud, models
from ..database import get_db
from ..utils import get_current_user
import re

# 注意：这里不写 prefix，因为我们在 main.py 里已经定义了 prefix="/api/service" 和 "/api/service-self"
router = APIRouter()
logger = logging.getLogger("uvicorn.error")


# -------------------------------------------
# 发布服务 (Service Create)
# -------------------------------------------
@router.post("/")  # 对应 /api/service/
def create_service(service_in: schemas.ServiceCreate, db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    # Validate need association if provided
    if getattr(service_in, 'needId', None):
        need = crud.get_need(db, int(service_in.needId))
        if not need:
            return {"code": 400, "msg": "关联的需求不存在", "data": None}
        # need.status: 0=已发布, other values mean closed/cancelled
        if int(getattr(need, 'status', 0)) != 0:
            return {"code": 400, "msg": "该需求已关闭或不可响应", "data": None}
        # If any accepted service exists for this need, block new responses
        services = crud.get_services_by_need(db, need.id)
        if any(s.get('status') == 1 for s in services):
            return {"code": 400, "msg": "该需求已有被接受的响应，无法再次提供服务", "data": None}

    # 调用 crud 创建
    new_service = crud.create_service(db, current_user.id, service_in)
    # 返回成功包
    return {"code": 200, "msg": "服务发布成功", "data": new_service.id}


# -------------------------------------------
# 获取我的服务列表 (My Service List)
# -------------------------------------------
@router.get("/my-list")  # 对应 /api/service-self/my-list
def my_service_list(request: Request, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Debug logging to help trace authentication issues
    try:
        auth_header = request.headers.get('authorization')
        logger.info(f"[SERVICE-MY-LIST] Authorization={auth_header} user={getattr(current_user, 'username', None)} id={getattr(current_user, 'id', None)}")
    except Exception as _e:
        logger.warning(f"[SERVICE-MY-LIST] logging failed: {_e}")

    # 1. 调用 crud 获取列表
    data = crud.get_my_service_list(db, current_user.id)
    # 2. 返回给前端（注意：不加 response_model，防止 422 错误）
    return {"code": 200, "msg": "ok", "data": data}


# -------------------------------------------
# 获取所有服务列表 (Service List - 公共)
# -------------------------------------------
@router.get("/list")  # 对应 /api/service/list
def service_list(
        keyword: str = None,
        serviceType: str = None,
        db: Session = Depends(get_db)
):
    # 调用 crud
    data = crud.get_service_list(db, keyword=keyword, service_type=serviceType)
    return {"code": 200, "msg": "ok", "data": data}


# -------------------------------------------
# 获取服务详情 (Detail) — 返回前端期望字段
# -------------------------------------------
@router.get("/detail/{service_id}")
def service_detail(service_id: str, db: Session = Depends(get_db)):
    # Accept both numeric ids and prefixed ids like 'service_123'
    m = re.search(r"(\d+)", str(service_id))
    if not m:
        # Return a structured 422 so client sees a clear message rather than FastAPI's type-conversion 422
        raise HTTPException(status_code=422, detail="无效的服务ID")
    sid = int(m.group(1))

    s = crud.get_service(db, sid)
    if not s:
        return {"code": 404, "msg": "服务不存在", "data": None}

    # 获取关联需求标题（如果存在）
    need_title = None
    if s.need_id:
        need = crud.get_need(db, s.need_id)
        need_title = need.title if need else None

    # try to resolve publisher username from relationship first, fallback to DB lookup
    owner_username = None
    try:
        owner_username = s.owner.username if getattr(s, 'owner', None) and getattr(s.owner, 'username', None) else None
    except Exception:
        owner_username = None

    if not owner_username and getattr(s, 'owner_id', None):
        try:
            user = crud.get_user_by_id(db, s.owner_id)
            owner_username = user.username if user else None
        except Exception:
            owner_username = None

    if not owner_username:
        owner_username = ''

    # files stored as JSON
    files = s.files if s.files else []

    data = {
        "id": s.id,
        "needId": s.need_id,
        "needTitle": need_title,
        "serviceType": s.service_type,
        "title": s.title,
        "content": s.content,
        "files": files,
        "status": int(s.status) if s.status is not None else 0,
        "userId": s.owner_id,
        "userName": owner_username,
        "createTime": s.create_time
    }
    return {"code": 200, "msg": "ok", "data": data}


# -------------------------------------------
# 更新服务 (Update Service) - 仅限拥有者
# -------------------------------------------
@router.put("/{service_id}")
def update_service(service_id: int, service_in: schemas.ServiceCreate, db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    # Only owner may update
    res = crud.update_service(db, service_id, current_user.id, service_in)
    if res is None:
        return {"code": 404, "msg": "服务不存在", "data": None}
    if res is False:
        return {"code": 403, "msg": "无权限修改", "data": None}
    return {"code": 200, "msg": "修改成功", "data": None}


# -------------------------------------------
# 列出某个需求的所有响应（服务自荐）
# -------------------------------------------
@router.get('/by-need/{need_id}')
def services_by_need(need_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # return list of services for a need (include publisher username)
    data = crud.get_services_by_need(db, need_id)
    return {"code": 200, "msg": "ok", "data": data}


# -------------------------------------------
# 确认（接受）某条响应，仅限需求发布者
# -------------------------------------------
@router.put('/confirm/{service_id}')
def confirm_service(service_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    res = crud.accept_service(db, service_id, current_user.id)
    if res is None:
        return {"code": 404, "msg": "响应不存在", "data": None}
    if res is False:
        return {"code": 403, "msg": "无权限或该响应不属于你的需求", "data": None}
    return {"code": 200, "msg": "确认成功", "data": None}


# -------------------------------------------
# 拒绝某条响应，仅限需求发布者
# -------------------------------------------
@router.put('/reject/{service_id}')
def reject_service_endpoint(service_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    res = crud.reject_service(db, service_id, current_user.id)
    if res is None:
        return {"code": 404, "msg": "响应不存在", "data": None}
    if res is False:
        return {"code": 403, "msg": "无权限或该响应不属于你的需求", "data": None}
    return {"code": 200, "msg": "拒绝成功", "data": None}

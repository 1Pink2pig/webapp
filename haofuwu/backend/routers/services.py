from fastapi import APIRouter, Depends, HTTPException, Query, Request
import logging
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud, models
from ..database import get_db
from ..utils import get_current_user

# 注意：这里不写 prefix，因为我们在 main.py 里已经定义了 prefix="/api/service" 和 "/api/service-self"
router = APIRouter()
logger = logging.getLogger("uvicorn.error")


# -------------------------------------------
# 发布服务 (Service Create)
# -------------------------------------------
@router.post("/")  # 对应 /api/service/
def create_service(service_in: schemas.ServiceCreate, db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
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
def service_detail(service_id: int, db: Session = Depends(get_db)):
    s = crud.get_service(db, service_id)
    if not s:
        return {"code": 404, "msg": "服务不存在", "data": None}

    # 获取关联需求标题（如果存在）
    need_title = None
    if s.need_id:
        need = crud.get_need(db, s.need_id)
        need_title = need.title if need else None

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
        "createTime": s.create_time
    }
    return {"code": 200, "msg": "ok", "data": data}
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud, models
from ..database import get_db
from ..utils import get_current_user

# 注意：这里不写 prefix，因为我们在 main.py 里已经定义了 prefix="/api/service" 和 "/api/service-self"
router = APIRouter()


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
def my_service_list(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
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
# 获取服务详情 (Detail)
# -------------------------------------------
@router.get("/detail/{service_id}")
def service_detail(service_id: int, db: Session = Depends(get_db)):
    s = crud.get_service(db, service_id)
    if not s:
        return {"code": 404, "msg": "服务不存在", "data": None}

    # 手动转成 Schema 格式返回
    data = schemas.ServiceOut(
        id=s.id,
        need_id=s.need_id,
        title=s.title,
        service_type=s.service_type,
        content=s.content,
        status=s.status,
        user_id=s.owner_id,
        create_time=s.create_time
    )
    return {"code": 200, "msg": "ok", "data": data}
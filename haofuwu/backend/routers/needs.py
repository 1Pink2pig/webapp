from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud, models
from ..database import get_db
from ..utils import get_current_user

router = APIRouter()


# ==========================================
# 1. 发布需求 (兼容新旧两种写法)
# ==========================================

# 新写法: POST /api/need/
@router.post("/", response_model=schemas.NeedOut)
def create_need(need_in: schemas.NeedCreate, db: Session = Depends(get_db),
                current_user: models.User = Depends(get_current_user)):
    # 调用 crud 创建并返回序列化的 NeedOut，避免直接返回 ORM 对象导致 response validation 失败
    n = crud.create_need(db, current_user.id, need_in)

    img_list = n.img_urls if getattr(n, 'img_urls', None) else []

    return schemas.NeedOut(
        id=n.id,
        title=n.title,
        description=n.description,
        region=n.region,
        serviceType=n.service_type,
        imgUrls=img_list,
        videoUrl=n.video_url,
        status=int(n.status) if n.status is not None else 0,
        hasResponse=False,
        userId=n.owner_id,
        userName=current_user.username,
        createTime=n.create_time
    )


# ==========================================
# 2. 获取需求列表
# ==========================================
@router.get("/", response_model=List[schemas.NeedOut])
def list_needs(
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    skip = (page - 1) * size
    return crud.get_needs(db, skip=skip, limit=size)


# ==========================================
# 3. 获取“我的”需求列表（支持分页和筛选）
# ==========================================
@router.get("/my-list")
def my_needs(
        pageNum: int = Query(1, ge=1),
        pageSize: int = Query(15, ge=1, le=200),
        keyword: str = None,
        serviceType: str = None,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    # 获取所有匹配的需求
    all_needs = crud.get_needs_my_list(db, current_user.id, keyword=keyword, service_type=serviceType)
    total = len(all_needs)
    # 简单分页
    start = (pageNum - 1) * pageSize
    end = start + pageSize
    records = all_needs[start:end]
    return {"code": 200, "msg": "ok", "data": {"records": records, "total": total}}


# ==========================================
# 4. 获取需求详情
# ==========================================
@router.get("/detail/{need_id}")
def need_detail(need_id: int, db: Session = Depends(get_db)):
    n = crud.get_need(db, need_id)
    if not n:
        return {"code": 404, "msg": "需求未找到", "data": None}

    # img_urls is stored as JSON (list) in the model
    img_list = n.img_urls if n.img_urls else []
    # try to get publisher username from relationship
    publish_username = None
    try:
        publish_username = n.owner.username if getattr(n, 'owner', None) else None
    except Exception:
        publish_username = None
    data = {
        "id": n.id,
        "title": n.title,
        "description": n.description,
        "region": n.region,
        "serviceType": n.service_type,
        "imgUrls": img_list,
        "videoUrl": n.video_url,
        "status": int(n.status) if n.status is not None else 0,
        "userId": n.owner_id,
        "userName": publish_username,
        "createTime": n.create_time
    }
    return {"code": 200, "msg": "ok", "data": data}


# ==========================================
# 5. 修改需求 (PUT /api/need/{id})
# ==========================================
@router.put("/{need_id}")
def update_need(need_id: int, need_in: schemas.NeedCreate, db: Session = Depends(get_db),
                current_user: models.User = Depends(get_current_user)):
    n = crud.get_need(db, need_id)
    if not n:
        return {"code": 404, "msg": "需求未找到", "data": None}
    if n.owner_id != current_user.id:
        return {"code": 403, "msg": "无权限", "data": None}

    crud.update_need(db, need_id, need_in)
    return {"code": 200, "msg": "修改成功", "data": None}


# ==========================================
# 6. 删除需求
# ==========================================
@router.delete("/{need_id}")
def delete_need(need_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    n = crud.get_need(db, need_id)
    if not n:
        return {"code": 404, "msg": "需求未找到", "data": None}
    if n.owner_id != current_user.id:
        return {"code": 403, "msg": "无权限", "data": None}

    crud.delete_need(db, need_id)
    return {"code": 200, "msg": "删除成功", "data": None}
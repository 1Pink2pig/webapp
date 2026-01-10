from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud, models
from ..database import get_db
from ..utils import get_current_user
import logging
import json

logger = logging.getLogger("uvicorn.error")

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
    needs = crud.get_needs(db, skip=skip, limit=size)
    # augment each NeedOut with hasAccepted
    results = []
    for n in needs:
        # determine if any service for this need has been accepted
        svc_list = crud.get_services_by_need(db, n.id)
        has_accepted = any(s.get('status') == 1 for s in svc_list)
        obj = n.dict() if hasattr(n, 'dict') else n
        obj['hasAccepted'] = has_accepted
        results.append(obj)
    return results


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
    # for each need, tag hasAccepted
    for n in all_needs:
        svc_list = crud.get_services_by_need(db, n.id)
        n.hasAccepted = any(s.get('status') == 1 for s in svc_list)
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
    try:
        n = crud.get_need(db, need_id)
        if not n:
            return {"code": 404, "msg": "需求未找到", "data": None}

        # Normalize img_urls: may be None, list, or legacy string
        img_list = n.img_urls if getattr(n, 'img_urls', None) else []
        if isinstance(img_list, str):
            # try JSON decode, else split by comma
            try:
                img_list = json.loads(img_list)
            except Exception:
                img_list = img_list.split(',') if img_list else []

        # try to get publisher username from relationship, fallback to DB lookup
        publish_username = None
        try:
            publish_username = n.owner.username if getattr(n, 'owner', None) and getattr(n.owner, 'username', None) else None
        except Exception:
            publish_username = None

        if not publish_username and getattr(n, 'owner_id', None):
            try:
                user = crud.get_user_by_id(db, n.owner_id)
                publish_username = user.username if user else None
            except Exception:
                publish_username = None

        # ensure we always return a string (avoid None) so frontend won't fallback to mock 'admin'
        if not publish_username:
            publish_username = ''

        data = {
            # provide both `id` and `needId` so frontend (which expects `needId`) works
            "id": n.id,
            "needId": n.id,
            "title": n.title,
            "description": n.description,
            "region": n.region,
            "serviceType": n.service_type,
            "imgUrls": img_list,
            "videoUrl": n.video_url,
            # return status as string to be compatible with frontend comparisons (e.g. '0')
            "status": str(int(n.status) if n.status is not None else 0),
            # indicate whether there are any responses attached to this need
            "hasResponse": bool(getattr(n, 'responses', None) and len(n.responses) > 0),
            "userId": n.owner_id,
            "userName": publish_username,
            "createTime": n.create_time,
            # include updateTime which the frontend displays
            "updateTime": getattr(n, 'update_time', None)
        }
        return {"code": 200, "msg": "ok", "data": data}
    except Exception as e:
        logger.exception(f"Error in need_detail for id={need_id}: %s", e)
        return {"code": 500, "msg": "服务器内部错误：无法获取需求详情", "data": None}


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
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db
# 👇 多加了一个 get_password_hash
from ..utils import get_current_user, get_password_hash

router = APIRouter()


@router.get("/me", response_model=schemas.UserOut)
def read_my_profile(current_user: models.User = Depends(get_current_user)):
    # 返回前端期望的 camelCase 用户对象（直接对象，便于前端登录后直接使用）
    return {
        "userId": current_user.id,
        "id": current_user.id,
        "username": current_user.username,
        "realName": current_user.full_name or "",
        "phone": current_user.phone or "",
        "intro": current_user.intro or "",
        "userType": current_user.user_type or "普通用户",
        "registerTime": current_user.register_time.isoformat() if getattr(current_user, 'register_time', None) else None,
        "updateTime": current_user.update_time.isoformat() if getattr(current_user, 'update_time', None) else None
    }


@router.put("/me", response_model=schemas.UserOut)
def update_my_profile(data: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if getattr(data, 'realName', None) is not None:
        user.full_name = data.realName
    if getattr(data, 'phone', None) is not None:
        user.phone = data.phone
    if getattr(data, 'email', None) is not None:
        user.email = data.email
    if getattr(data, 'intro', None) is not None:
        user.intro = data.intro
    user.update_time = __import__('datetime').datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "userId": user.id,
        "id": user.id,
        "username": user.username,
        "realName": user.full_name or "",
        "phone": user.phone or "",
        "intro": user.intro or "",
        "userType": user.user_type or "普通用户",
        "registerTime": user.register_time.isoformat() if getattr(user, 'register_time', None) else None,
        "updateTime": user.update_time.isoformat() if getattr(user, 'update_time', None) else None
    }


@router.get('/detail/{user_id}')
def get_user_detail(user_id: int, db: Session = Depends(get_db)):
    from ..crud import get_user_by_id
    user = get_user_by_id(db, user_id)
    if not user:
        return {"code": 404, "msg": "用户未找到", "data": None}
    # 返回兼容前端的字段结构（前端期望 username, realName 等）
    data = {
        "userId": user.id,
        "id": user.id,
        "username": user.username,
        "realName": user.full_name or "",
        "userType": user.user_type or "普通用户",
        "registerTime": user.register_time.isoformat() if getattr(user, 'register_time', None) else None,
        "updateTime": user.update_time.isoformat() if getattr(user, 'update_time', None) else None,
        "intro": user.intro or "",
        "phone": user.phone or ""
    }
    return {"code": 200, "msg": "ok", "data": data}


@router.get("/check-username")
def check_username(username: str, db: Session = Depends(get_db)):
    # 1. 查数据库
    user = db.query(models.User).filter(models.User.username == username).first()

    # 2. 打印日志
    print(f"👀 检查: {username} -> {'已占用' if user else '可用'}")

    # 3. 构造前端 validator.js 及其渴望的数据结构
    # 它在找 res.data.isUnique，所以 data 必须是一个字典

    if user:
        # 🛑 找到了 = 不唯一 (isUnique = False)
        return {
            "code": 200,
            "msg": "用户名已存在",
            "data": {
                "isUnique": False  # <--- 重点：包在字典里
            }
        }

    # ✅ 没找到 = 唯一 (isUnique = True)
    return {
        "code": 200,
        "msg": "用户名可用",
        "data": {
            "isUnique": True  # <--- 重点：包在字典里
        }
    }


@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. 虽然前端检查过了，后端为了安全再检查一遍用户名
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        return {"code": 400, "msg": "用户名已存在", "data": None}

    # 2. 密码加密 (这一步很重要，不能存明文密码)
    hashed_password = get_password_hash(user.password)

    # 3. 创建用户数据
    # 注意：前端传过来的是 realName，数据库里叫 full_name
    new_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        phone=user.phone,
        full_name=user.realName,  # 映射字段
        intro="",
        user_type="普通用户",  # 默认注册为普通用户
        register_time=__import__('datetime').datetime.now(),
        update_time=__import__('datetime').datetime.now()
    )

    # 4. 保存到数据库
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        # 5. 返回成功信息
        return {"code": 200, "msg": "注册成功", "data": new_user.id}
    except Exception as e:
        db.rollback()
        print(f"❌ 注册写入数据库失败: {e}")
        return {"code": 500, "msg": f"注册失败: {str(e)}", "data": None}
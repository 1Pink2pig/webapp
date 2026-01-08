from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, users, needs, services, upload
import os
from sqlalchemy import text

Base.metadata.create_all(bind=engine)

# 如果是旧的 SQLite 文件，可能缺少新增列；尝试在启动时补齐这些列，避免查询失败
try:
    with engine.connect() as conn:
        res = conn.execute(text("PRAGMA table_info('users')"))
        existing_cols = {row[1] for row in res.fetchall()} if res is not None else set()
        needed = {
            'phone': "TEXT",
            'intro': "TEXT",
            'user_type': "TEXT",
            'register_time': "DATETIME",
            'update_time': "DATETIME",
            'full_name': "TEXT"
        }
        for col, col_type in needed.items():
            if col not in existing_cols:
                try:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {col_type}"))
                except Exception:
                    # 忽略单条添加失败，继续尝试其它列
                    pass
except Exception:
    pass

app = FastAPI(title="haofuwu-backend")

# 开发时允许所有来源，避免跨域阻塞前端请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth")
app.include_router(users.router, prefix="/api/user")

app.include_router(users.router, prefix="/api")

app.include_router(needs.router, prefix="/api/need")

app.include_router(services.router, prefix="/api/service")

app.include_router(services.router, prefix="/api/service-self")
app.include_router(upload.router, prefix="/api/upload")

try:
    from .routers import service_self
    app.include_router(service_self.router, prefix="/api/service-self")
except Exception:
    pass

# include admin router (statistics) if available
try:
    from .routers import admin
    app.include_router(admin.router, prefix="/api/admin")
except Exception:
    # not critical in older setups
    pass


@app.get("/health")
def health():
    return {"status": "ok"}

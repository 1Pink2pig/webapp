# haofuwu-backend

FastAPI 后端，提供与前端对接的基本 API（用户、需求、服务、文件上传）。

运行：

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

数据库：使用 SQLite，文件 `haofuwu.db` 将生成在工作目录下。

前端默认运行在 http://localhost:8080，CORS 已允许该来源。

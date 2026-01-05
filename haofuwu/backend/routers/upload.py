import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    dest = os.path.join(UPLOAD_DIR, filename)
    try:
        with open(dest, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # 返回兼容前端的响应结构
    return JSONResponse({"code": 200, "msg": "ok", "data": {"filename": filename, "url": f"/uploads/{filename}"}})

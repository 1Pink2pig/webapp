from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas, crud, utils
from ..database import get_db
import traceback
import sys

router = APIRouter()


@router.post("/register")
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_username(db, user_in.username)
    if existing:
        return JSONResponse({"code": 400, "msg": "Username already registered", "data": None}, status_code=400)
    user = crud.create_user(db, user_in)
    return JSONResponse({"code": 200, "msg": "ok", "data": {"id": user.id, "username": user.username}})


@router.get('/check-username')
def check_username(username: str, db: Session = Depends(get_db)):
    try:
        existing = crud.get_user_by_username(db, username)
        return JSONResponse({"code": 200, "msg": "ok", "data": {"isUnique": existing is None}})
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return JSONResponse({"code": 500, "msg": f"check error: {str(e)}", "data": None}, status_code=500)


@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = utils.create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}

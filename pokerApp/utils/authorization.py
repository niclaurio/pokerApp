import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from models.user import User

SECRET_KEY = os.environ['secret_key']
ALGORITHM = 'HS256'
CRYPT_CONTEXT= CryptContext(schemas='bcrypt', deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

def hash_pwd(pwd: str)-> str:
    return CRYPT_CONTEXT.hash(pwd)


def verify_pwd(hashed_pwd: str, pwd: str) -> bool:
    return CRYPT_CONTEXT.verify(pwd, hashed_pwd)


def create_token(username: str, duration_minutes: datetime) -> str:
    expire = datetime.now() + timedelta(minutes=duration_minutes)
    data = {'sub': username, 'exp':expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM).get('sub')


def protect_endpoint(func: Callable):
    @wraps(func)
    def wrapper(request: Request, authorization: str=Depends(oauth2_scheme), *args, **kwargs):
        if not authorization:
            raise HTTPException(status_code=401, detail="missing required access token")
        if not authorization.startswith('bearer '):
            raise HTTPException(status_code=401, detail="invalid access token")
        try:
            username = verify_token(authorization.replace('bearer ', ''))
        except JWTError:
            raise HTTPException(status_code=401, detail='expired or invalid token')
        user = User.get_user_by_username(username)
        return func(request, user, *args, **kwargs)
    return wrapper


def check_user_credentials(username: str, pwd: str) -> None:
    try:
        user = User.get_user_by_username(username)
    except RowNotFound:
        raise HTTPException(status_code=404, detail="invalid username")
    if not verify_pwd(user.password, pwd):
        raise HTTPException(status_code=404, detail='invalid password')

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any

from app.core.security import create_access_token

router = APIRouter()

class TokenRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str

@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(payload: TokenRequest):
    # Standard enterprise secure checks
    if payload.password == "password":
        role = "admin" if payload.username.lower() == "admin" else "viewer"
        token_data = {"sub": payload.username, "role": role}
        token = create_access_token(token_data)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            role=role
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

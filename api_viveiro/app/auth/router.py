# app/auth/router.py
from datetime import timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Body, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr

from app.config import settings
from app.database import get_db
from app.models.funcionarios import Funcionario
from app.auth.jwt import create_access_token, get_current_user
from app.auth.utils import verificar_senha, gerar_senha_hash, validar_requisitos_senha
from app.crud import funcionarios as crud_funcionarios
from app.schemas.funcionarios import FuncionarioOut, FuncionarioPerfilUpdate
from app.schemas.auth import AuthMeOut, PermissionsOut
from app.auth.session import build_auth_me
from app.security.rbac import require_permission, resolve_permissions

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PasswordReset(BaseModel):
    old_password: str
    new_password: str

@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    result = await db.execute(select(Funcionario).where(Funcionario.usuario == form_data.username))
    user = result.scalars().first()
    
    if not user or not verificar_senha(form_data.password, user.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            data={"sub": user.usuario}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/reset-password", response_model=FuncionarioOut)
async def reset_password(
    password_data: PasswordReset,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("config.profile.edit")),
) -> Any:
    """
    Reset password for logged in user
    """
    user_id = current_user.id
    
    result = await db.execute(select(Funcionario).where(Funcionario.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    
    # Verificar senha atual
    if not verificar_senha(password_data.old_password, user.senha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta",
        )
    
    # Validar requisitos da nova senha
    valid, message = validar_requisitos_senha(password_data.new_password)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
    
    # Atualizar senha
    user.senha = gerar_senha_hash(password_data.new_password)
    await db.commit()
    await db.refresh(user)
    
    return FuncionarioOut.from_orm(user)

@router.get("/me", response_model=AuthMeOut)
async def read_users_me(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user),
    x_viveiro_id: Optional[int] = Header(None, alias="X-Viveiro-Id"),
) -> AuthMeOut:
    """
    Usuário logado + array `permissions` (SSOT) + contexto viveiro ativo.

    O frontend deve usar `permissions` para guards de rota/UI — não inferir
    acesso pelo campo `cargo` nem replicar a matriz RBAC localmente.
    Header X-Viveiro-Id: somente admin (validado no backend).
    """
    from app.security.viveiro_context import resolve_viveiro_context
    from app.auth.session import build_auth_me_async

    ctx = await resolve_viveiro_context(db, current_user, x_viveiro_id)
    return await build_auth_me_async(db, current_user, ctx)


@router.get("/permissions", response_model=PermissionsOut)
async def read_my_permissions(
    current_user: FuncionarioOut = Depends(get_current_user),
) -> PermissionsOut:
    """
    Permissões efetivas do usuário logado (refresh leve sem payload completo).
    """
    return PermissionsOut(permissions=sorted(resolve_permissions(current_user.perfis)))


@router.patch("/me", response_model=AuthMeOut)
async def update_users_me(
    perfil: FuncionarioPerfilUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("config.profile.edit")),
) -> AuthMeOut:
    """
    Atualiza dados básicos do perfil do usuário logado.

    FuncionarioPerfilUpdate não inclui `perfis` — tentativas de escalação
    via mass-assignment nesta rota são ignoradas por design (schema separado).
    """
    try:
        updated = await crud_funcionarios.update_funcionario_perfil(
            db, current_user.id, perfil
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    from app.security.viveiro_context import resolve_viveiro_context
    from app.auth.session import build_auth_me_async

    ctx = await resolve_viveiro_context(db, FuncionarioOut.from_orm(updated), None)
    return await build_auth_me_async(db, FuncionarioOut.from_orm(updated), ctx)

@router.post("/check-username")
async def check_username_available(
    username: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Check if a username is available
    """
    result = await db.execute(select(Funcionario).where(Funcionario.usuario == username))
    user = result.scalars().first()
    
    return {"available": user is None}

@router.post("/validate-password")
async def validate_password(
    password: str = Body(..., embed=True)
) -> Any:
    """
    Validate if a password meets security requirements
    """
    valid, message = validar_requisitos_senha(password)
    return {"valid": valid, "message": message}
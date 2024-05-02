from pydantic import EmailStr

from fastapi import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import exc
from sqlmodel import select

from ..generics.crud import CRUDBase
from ..generics.utils import security
from .models import User, Role
from .schemas import UserCreate, UserUpdate, RoleCreate, RoleUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def create(
        self, *, obj_in: UserCreate, db_session: AsyncSession | None = None
    ) -> User:
        db_session = db_session or super().get_db().session
        db_obj = User.model_validate(obj_in)
        db_obj.hashed_password = security.get_password_hash(obj_in.password)
        try:          
            db_session.add(db_obj)
            await db_session.commit()
        except exc.IntegrityError:
            await db_session.rollback()
            raise HTTPException(status_code=409, detail="Resource already exists")
        await db_session.refresh(db_obj)
        return db_obj
    
    async def get_by_email(
        self, *, email: str, db_session: AsyncSession | None = None
    ) -> User | None:
        db_session = db_session or super().get_db().session
        users = await db_session.execute(select(User).where(User.email == email))
        return users.scalar_one_or_none()

    async def authenticate(self, *, email: EmailStr, password: str) -> User | None:
        user = await self.get_by_email(email=email)
        if not user:
            return None
        if not security.verify_password(password, user.hashed_password):
            return None
        return user

class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    pass

user_crud = CRUDUser(User)
role_crud = CRUDRole(Role)

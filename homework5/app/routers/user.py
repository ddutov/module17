# Аннотации, Модели БД и Pydantic.
from typing import Annotated

# Функция подключения к БД
from backend.db_depends import get_db
from fastapi import APIRouter, Depends, status, HTTPException
from slugify import slugify
from sqlalchemy import insert
# Функции работы с записями.
from sqlalchemy import select, update, delete
# Сессия БД
from sqlalchemy.orm import Session

from models import User, Task
from schemas import CreateUser, UpdateUser

# Функция создания slug-строки

router = APIRouter(prefix='/user', tags=['user'])


@router.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router.get('/user_id')
async def user_by_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalars(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no user found'
        )
    return user


@router.post('/create')
async def create_user(db: Annotated[Session, Depends(get_db)], create_user: CreateUser):
    db.execute(insert(User).values(username=create_user.username,
                                   firstname=create_user.firstname,
                                   lastname=create_user.lastname,
                                   age=create_user.age,
                                   slug=slugify(create_user.username)))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put('/update')
async def update_user(db: Annotated[Session, Depends(get_db)], user_id: int, update_user: UpdateUser):
    user = db.scalars(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found"'
        )
    db.execute(update(User).where(User.id == user_id).values(
        firstname=update_user.firstname,
        lastname=update_user.lastname,
        age=update_user.age,
        slug=slugify(update_user.id)
    ))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'User update is successful'
    }


@router.delete('/delete')
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalars(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no user found'
        )
    db.execute(delete(User).where(User.id == user_id))
    db.execute(delete(Task).where(Task.user_id == user_id))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User delete is successful'
    }


@router.get('/user_id/tasks')
async def tasks_by_user_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    task = db.scalars(select(Task).where(Task.user_id == user_id))
    return task

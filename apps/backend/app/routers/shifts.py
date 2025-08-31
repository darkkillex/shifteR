from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_session
from .. import models, schemas
router=APIRouter(prefix='/shifts', tags=['shifts'])
@router.get('', response_model=list[schemas.ShiftTemplateOut])
async def list_shifts(session:AsyncSession=Depends(get_session)):
    res=await session.execute(select(models.ShiftTemplate).order_by(models.ShiftTemplate.code)); return res.scalars().all()

from __future__ import annotations
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_session
from .. import models
from ..services.rotation import generate_rotation, RotationKind
router=APIRouter(prefix='/rotation', tags=['rotation'])
class RotationRequest(BaseModel):
    employee_ids:list[int]=Field(..., min_items=1)
    kind:RotationKind
    range_start:date; range_end:date
    offset_strategy:str='round_robin'; dry_run:bool=False
class RotationResult(BaseModel):
    created:int; details:dict[int,int]
@router.post('/generate', response_model=RotationResult)
async def generate(req:RotationRequest, session:AsyncSession=Depends(get_session)):
    if req.range_start>req.range_end: raise HTTPException(400,'Invalid range')
    emps=(await session.execute(select(models.Employee).where(models.Employee.id.in_(req.employee_ids)))).scalars().all()
    if len(emps)!=len(set(req.employee_ids)): raise HTTPException(404,'One or more employees not found')
    details={}
    for idx,emp_id in enumerate(req.employee_ids):
        offset=idx if req.offset_strategy=='round_robin' else 0
        plan=generate_rotation(req.kind, req.range_start, req.range_end, offset_days=offset)
        count=0
        for d,token in plan.items():
            stmt=select(models.ScheduleEntry).where(models.ScheduleEntry.employee_id==emp_id, models.ScheduleEntry.date==d)
            existing=(await session.execute(stmt)).scalars().first()
            if existing: existing.shift_code=token; existing.leave_type=None
            else: session.add(models.ScheduleEntry(employee_id=emp_id, date=d, shift_code=token, leave_type=None))
            count+=1
        details[emp_id]=count
    if not req.dry_run: await session.commit()
    return RotationResult(created=sum(details.values()), details=details)

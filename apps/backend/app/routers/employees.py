from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_session
from .. import models, schemas
router=APIRouter(prefix='/employees',tags=['employees'])
@router.get('', response_model=list[schemas.EmployeeOut])
async def list_employees(session:AsyncSession=Depends(get_session)):
    res=await session.execute(select(models.Employee).order_by(models.Employee.last_name, models.Employee.first_name)); return res.scalars().all()
@router.post('', response_model=schemas.EmployeeOut, status_code=201)
async def create_employee(payload:schemas.EmployeeCreate, session:AsyncSession=Depends(get_session)):
    emp=models.Employee(first_name=payload.first_name,last_name=payload.last_name,company=payload.company,email=payload.email)
    session.add(emp); await session.commit(); await session.refresh(emp); return emp
@router.get('/{employee_id}', response_model=schemas.EmployeeOut)
async def get_employee(employee_id:int, session:AsyncSession=Depends(get_session)):
    emp=await session.get(models.Employee, employee_id)
    if not emp: raise HTTPException(404,'Employee not found')
    return emp

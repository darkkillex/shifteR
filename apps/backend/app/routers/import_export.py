from __future__ import annotations
from datetime import date
from io import StringIO
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_session
from .. import models

router = APIRouter(prefix="/io", tags=["import-export"])

@router.get("/export.csv")
async def export_csv(range_start: date, range_end: date, session: AsyncSession = Depends(get_session)):
    stmt = (
        select(models.ScheduleEntry, models.Employee)
        .join(models.Employee, models.Employee.id == models.ScheduleEntry.employee_id)
        .where(models.ScheduleEntry.date >= range_start, models.ScheduleEntry.date <= range_end)
        .order_by(models.Employee.last_name, models.Employee.first_name, models.ScheduleEntry.date)
    )
    buf = StringIO()
    buf.write("employee_id,first_name,last_name,company,email,date,token\n")
    for entry, emp in (await session.execute(stmt)).all():
        token = entry.leave_type or entry.shift_code or ""
        buf.write(f"{emp.id},{emp.first_name},{emp.last_name},{emp.company},{emp.email},{entry.date},{token}\n")
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=schedule_{range_start}_{range_end}.csv"},
    )

@router.post("/import.csv")
async def import_csv(file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Upload a .csv file")
    content = (await file.read()).decode("utf-8")
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    if not lines or not lines[0].lower().startswith("employee_id"):
        raise HTTPException(400, "CSV header must be: employee_id,first_name,last_name,company,email,date,token")

    count = 0
    for row in lines[1:]:
        parts = row.split(",")
        if len(parts) < 7:
            continue

        emp_id_str = parts[0]
        d_str = parts[5]
        token = ",".join(parts[6:])

        d = date.fromisoformat(d_str)
        emp_id = int(emp_id_str)

        from sqlalchemy import and_, select as s
        stmt = s(models.ScheduleEntry).where(
            and_(models.ScheduleEntry.employee_id == emp_id, models.ScheduleEntry.date == d)
        )
        existing = (await session.execute(stmt)).scalars().first()

        shift_code = token if token and token not in ("VACATION", "PTO") else None
        leave_type = token if token in ("VACATION", "PTO") else None

        if existing:
            existing.shift_code = shift_code
            existing.leave_type = leave_type
        else:
            session.add(
                models.ScheduleEntry(employee_id=emp_id, date=d, shift_code=shift_code, leave_type=leave_type)
            )
        count += 1

    await session.commit()
    return PlainTextResponse(f"Imported {count} rows")

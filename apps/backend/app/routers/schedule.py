from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from ..database import get_session
from .. import models, schemas
from ..utils import diff as diffutil
from ..utils.ics import generate_ics
from ..utils.mailer import send_email_async
router=APIRouter(prefix='/schedule', tags=['schedule'])
@router.get('/entries', response_model=list[schemas.ScheduleEntryOut])
async def list_entries(range_start:date, range_end:date, session:AsyncSession=Depends(get_session)):
    stmt=select(models.ScheduleEntry).where(and_(models.ScheduleEntry.date>=range_start, models.ScheduleEntry.date<=range_end))
    res=await session.execute(stmt); return res.scalars().all()
@router.post('/entries', response_model=schemas.ScheduleEntryOut, status_code=201)
async def upsert_entry(payload:schemas.ScheduleEntryCreate, session:AsyncSession=Depends(get_session)):
    stmt=select(models.ScheduleEntry).where(and_(models.ScheduleEntry.employee_id==payload.employee_id, models.ScheduleEntry.date==payload.date))
    existing=(await session.execute(stmt)).scalars().first()
    if existing:
        existing.shift_code=payload.shift_code; existing.leave_type=payload.leave_type
        await session.commit(); await session.refresh(existing); return existing
    entry=models.ScheduleEntry(employee_id=payload.employee_id, date=payload.date, shift_code=payload.shift_code, leave_type=payload.leave_type)
    session.add(entry); await session.commit(); await session.refresh(entry); return entry
@router.post('/publish', response_model=schemas.PublishResult)
async def publish(payload:schemas.PublishRequest, session:AsyncSession=Depends(get_session)):
    if payload.range_start>payload.range_end: raise HTTPException(400,'Invalid range')
    entries_stmt=select(models.ScheduleEntry).where(and_(models.ScheduleEntry.date>=payload.range_start, models.ScheduleEntry.date<=payload.range_end))
    cur_entries=(await session.execute(entries_stmt)).scalars().all()
    last_snap_stmt=select(models.PlanSnapshot).order_by(models.PlanSnapshot.id.desc()).limit(1)
    last_snap=(await session.execute(last_snap_stmt)).scalars().first()
    prev_items_by_emp={}
    if last_snap:
        items_stmt=select(models.PlanSnapshotItem).where(and_(models.PlanSnapshotItem.snapshot_id==last_snap.id, models.PlanSnapshotItem.date>=payload.range_start, models.PlanSnapshotItem.date<=payload.range_end))
        items=(await session.execute(items_stmt)).scalars().all()
        for it in items:
            token=it.leave_type or it.shift_code
            prev_items_by_emp.setdefault(it.employee_id, []).append((it.date, token))
    cur_by_emp={}
    for e in cur_entries:
        token=e.leave_type or e.shift_code
        cur_by_emp.setdefault(e.employee_id, []).append((e.date, token))
    affected=[]; diffs={}
    for emp_id, items in cur_by_emp.items():
        prev=prev_items_by_emp.get(emp_id, [])
        dsum=diffutil.compute_employee_diff(prev, items)
        if dsum.added or dsum.removed or dsum.changed:
            affected.append(emp_id); diffs[emp_id]=dsum
    snap=models.PlanSnapshot(range_start=payload.range_start, range_end=payload.range_end, author='system', note=payload.note)
    session.add(snap); await session.flush()
    for e in cur_entries:
        session.add(models.PlanSnapshotItem(snapshot_id=snap.id, employee_id=e.employee_id, date=e.date, shift_code=e.shift_code, leave_type=e.leave_type))
    await session.commit()
    if affected:
        emps=(await session.execute(select(models.Employee).where(models.Employee.id.in_(affected)))).scalars().all(); emp_map={x.id:x for x in emps}
        shifts=(await session.execute(select(models.ShiftTemplate))).scalars().all(); shift_map={s.code:s for s in shifts}
        for emp_id in affected:
            emp=emp_map[emp_id]; dsum=diffs[emp_id]
            def fmt_token(t):
                if not t: return '—'
                if t in shift_map:
                    s=shift_map[t]; return f"{s.name} ({s.start_hhmm}-{s.end_hhmm})"
                return t
            rows=[]
            for d,v in dsum.added: rows.append(f"<tr><td>{d}</td><td>aggiunto</td><td>{fmt_token(v)}</td><td></td></tr>")
            for d,v in dsum.removed: rows.append(f"<tr><td>{d}</td><td>rimosso</td><td>{fmt_token(v)}</td><td></td></tr>")
            for d,pv,nv in dsum.changed: rows.append(f"<tr><td>{d}</td><td>modificato</td><td>{fmt_token(pv)}</td><td>{fmt_token(nv)}</td></tr>")
            html=(
                f"<h3>Aggiornamento turni ({payload.range_start} -> {payload.range_end})</h3>"+
                f"<p>Ciao {emp.full_name} ({emp.company}), ecco le modifiche rispetto alla versione precedente:</p>"+
                "<table border=1 cellpadding=6 cellspacing=0><thead><tr><th>Data</th><th>Azione</th><th>Prima</th><th>Dopo</th></tr></thead>"+
                f"<tbody>{''.join(rows)}</tbody></table><p>In allegato trovi anche il calendario (.ics) del periodo.</p>"
            )
            cur_items=cur_by_emp.get(emp_id, []); ics_items=[]
            for d,token in cur_items:
                if token and token in shift_map:
                    s=shift_map[token]; ics_items.append({'date':d,'title':s.name,'start_hhmm':s.start_hhmm,'end_hhmm':s.end_hhmm,'overnight':s.overnight})
                elif token and token in ('VACATION','PTO'):
                    ics_items.append({'date':d,'title':token,'start_hhmm':'00:00','end_hhmm':'23:59','overnight':False})
            ics_str=generate_ics(emp.full_name, ics_items)
            await send_email_async(emp.email, 'Aggiornamento piano turni', html, [(f"turni_{payload.range_start}_{payload.range_end}.ics", ics_str.encode('utf-8'))])
    return schemas.PublishResult(snapshot_id=snap.id, affected_employees=affected)

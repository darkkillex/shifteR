import asyncio
from datetime import date,timedelta
from .database import AsyncSessionLocal, engine, Base
from .models import Employee, ScheduleEntry
from .utils.seed import ensure_shift_templates
async def main():
    async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as s:
        await ensure_shift_templates(s)
        emps=[Employee(first_name='Mario',last_name='Rossi',company='ACME',email='mario.rossi@acme.it'),Employee(first_name='Luca',last_name='Bianchi',company='ACME',email='luca.bianchi@acme.it'),Employee(first_name='Giulia',last_name='Verdi',company='BetaSpa',email='giulia.verdi@betaspa.it')]
        s.add_all(emps); await s.commit()
        for e in emps: await s.refresh(e)
        today=date.today()
        for i in range(7): s.add(ScheduleEntry(employee_id=emps[0].id, date=today+timedelta(days=i), shift_code='D_8_17'))
        await s.commit(); print('Seed completed.')
if __name__=='__main__': asyncio.run(main())

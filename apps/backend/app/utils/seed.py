from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import ShiftTemplate
DEFAULT_SHIFTS=[('D_8_17','Giornaliero 8-17','08:00','17:00',False),('H16_A','H16 – 6-14','06:00','14:00',False),('H16_B','H16 – 14-22','14:00','22:00',False),('H24_A','H24 – 6-14','06:00','14:00',False),('H24_B','H24 – 14-22','14:00','22:00',False),('H24_C','H24 – 22-6','22:00','06:00',True),('H16_7x7_A','H16 7on7off – 6-14','06:00','14:00',False),('H16_7x7_B','H16 7on7off – 14-22','14:00','22:00',False),('H24_7x7_A','H24 7on7off – 7-19','07:00','19:00',False),('H24_7x7_B','H24 7on7off – 19-7','19:00','07:00',True)]
async def ensure_shift_templates(session: AsyncSession)->None:
    existing=(await session.execute(select(ShiftTemplate.code))).scalars().all()
    to_add=[s for s in DEFAULT_SHIFTS if s[0] not in set(existing)]
    for code,name,start,end,overnight in to_add:
        session.add(ShiftTemplate(code=code,name=name,start_hhmm=start,end_hhmm=end,overnight=overnight))
    if to_add: await session.commit()

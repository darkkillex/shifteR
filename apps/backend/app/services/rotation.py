from __future__ import annotations
from datetime import date,timedelta
from typing import Literal
RotationKind=Literal['H16_4on2off','H24_4on2off','H16_7on7off','H24_7on7off','DAY_8_17']
SHIFT_BY_TOKEN={'D_8_17':'D_8_17','H16_A':'H16_A','H16_B':'H16_B','H24_A':'H24_A','H24_B':'H24_B','H24_C':'H24_C','H16_7x7_A':'H16_7x7_A','H16_7x7_B':'H16_7x7_B','H24_7x7_A':'H24_7x7_A','H24_7x7_B':'H24_7x7_B'}

def daterange(d1:date,d2:date):
    cur=d1
    while cur<=d2:
        yield cur; cur+=timedelta(days=1)

def generate_rotation(kind:RotationKind,start:date,end:date,offset_days:int=0)->dict[date,str]:
    out:dict[date,str]={}
    if kind=='DAY_8_17':
        for d in daterange(start,end):
            if d.weekday()<5: out[d]=SHIFT_BY_TOKEN['D_8_17']
        return out
    if kind in ('H16_4on2off','H24_4on2off'):
        pattern_len=6
        day_shifts=['H16_A','H16_B','H16_A','H16_B'] if kind=='H16_4on2off' else ['H24_A','H24_B','H24_C','H24_A']
        for idx,d in enumerate(daterange(start,end)):
            k=(idx+offset_days)%pattern_len
            if k<4: out[d]=SHIFT_BY_TOKEN[day_shifts[k%len(day_shifts)]]
        return out
    if kind=='H16_7on7off':
        for idx,d in enumerate(daterange(start,end)):
            k=(idx+offset_days)%14
            if k<7: out[d]=SHIFT_BY_TOKEN['H16_A' if k%2==0 else 'H16_B']
        return out
    if kind=='H24_7on7off':
        for idx,d in enumerate(daterange(start,end)):
            k=(idx+offset_days)%14
            if k<7: out[d]=SHIFT_BY_TOKEN['H24_7x7_A' if k%2==0 else 'H24_7x7_B']
        return out
    raise ValueError(f'Unsupported rotation kind: {kind}')

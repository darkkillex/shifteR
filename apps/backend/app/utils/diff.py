from datetime import date
from typing import Iterable
class DiffSummary:
    def __init__(self):
        self.added=[]; self.removed=[]; self.changed=[]

def _index(items: Iterable[tuple[date, str|None]]):
    return {d:v for d,v in items}

def compute_employee_diff(prev_items: Iterable[tuple[date, str|None]], new_items: Iterable[tuple[date, str|None]]):
    prev=_index(prev_items); new=_index(new_items); out=DiffSummary(); all_days=set(prev)|set(new)
    for d in sorted(all_days):
        pv=prev.get(d); nv=new.get(d)
        if pv is None and nv is not None: out.added.append((d,nv))
        elif pv is not None and nv is None: out.removed.append((d,pv))
        elif pv!=nv: out.changed.append((d,pv,nv))
    return out

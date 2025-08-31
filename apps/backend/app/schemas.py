from datetime import date
from pydantic import BaseModel, EmailStr
class EmployeeCreate(BaseModel):
    first_name: str; last_name: str; company: str; email: EmailStr
class EmployeeOut(BaseModel):
    id:int; first_name:str; last_name:str; company:str; email:EmailStr; is_active:bool; full_name:str
    class Config: from_attributes=True
class ShiftTemplateOut(BaseModel):
    code:str; name:str; start_hhmm:str; end_hhmm:str; overnight:bool
    class Config: from_attributes=True
class ScheduleEntryCreate(BaseModel):
    employee_id:int; date:date; shift_code:str|None=None; leave_type:str|None=None
class ScheduleEntryOut(BaseModel):
    id:int; employee_id:int; date:date; shift_code:str|None; leave_type:str|None
    class Config: from_attributes=True
class PublishRequest(BaseModel):
    range_start:date; range_end:date; note:str|None=None
class PublishResult(BaseModel):
    snapshot_id:int; affected_employees:list[int]

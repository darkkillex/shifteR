from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, Date, DateTime, ForeignKey, UniqueConstraint, text
from .database import Base
class Employee(Base):
    __tablename__='employees'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    company: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text('true'))
    schedule_entries: Mapped[list['ScheduleEntry']] = relationship(back_populates='employee')
    @property
    def full_name(self) -> str: return f"{self.first_name} {self.last_name}".strip()
class ShiftTemplate(Base):
    __tablename__='shift_templates'
    code: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    start_hhmm: Mapped[str] = mapped_column(String(5))
    end_hhmm: Mapped[str] = mapped_column(String(5))
    overnight: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
class ScheduleEntry(Base):
    __tablename__='schedule_entries'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.id', ondelete='CASCADE'))
    date: Mapped[Date] = mapped_column(Date, index=True)
    shift_code: Mapped[str | None] = mapped_column(ForeignKey('shift_templates.code'), nullable=True)
    leave_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    employee: Mapped['Employee'] = relationship(back_populates='schedule_entries')
    shift: Mapped[ShiftTemplate | None] = relationship()
    __table_args__ = (UniqueConstraint('employee_id','date', name='uq_employee_date'),)
class PlanSnapshot(Base):
    __tablename__='plan_snapshots'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('NOW()'))
    range_start: Mapped[Date] = mapped_column(Date)
    range_end: Mapped[Date] = mapped_column(Date)
    author: Mapped[str | None] = mapped_column(String(120))
    note: Mapped[str | None] = mapped_column(String(500))
    items: Mapped[list['PlanSnapshotItem']] = relationship(back_populates='snapshot', cascade='all, delete-orphan')
class PlanSnapshotItem(Base):
    __tablename__='plan_snapshot_items'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey('plan_snapshots.id', ondelete='CASCADE'))
    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.id', ondelete='CASCADE'))
    date: Mapped[Date] = mapped_column(Date, index=True)
    shift_code: Mapped[str | None] = mapped_column(String(32))
    leave_type: Mapped[str | None] = mapped_column(String(20))
    snapshot: Mapped['PlanSnapshot'] = relationship(back_populates='items')

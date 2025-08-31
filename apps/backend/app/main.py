from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .settings import settings
from .database import engine, Base, AsyncSessionLocal
from .routers import health, employees, shifts, schedule
from .routers import rotation as rotation_router
from .routers import import_export as io_router
from .utils.seed import ensure_shift_templates
app=FastAPI(title=settings.APP_NAME)
app.add_middleware(CORSMiddleware, allow_origins=[settings.FRONTEND_URL,'http://localhost:5173'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
@app.on_event('startup')
async def on_startup():
    async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as s: await ensure_shift_templates(s)
app.include_router(health.router, prefix='/api')
app.include_router(employees.router, prefix='/api')
app.include_router(shifts.router, prefix='/api')
app.include_router(schedule.router, prefix='/api')
app.include_router(rotation_router.router, prefix='/api')
app.include_router(io_router.router, prefix='/api')

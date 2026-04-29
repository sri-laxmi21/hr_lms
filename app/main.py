from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.database import engine, Base

# ======================
# IMPORT MODELS (IMPORTANT)
# ======================
from app.models import (
    user_m, role_m, organization_m, branch_m, menu_m, role_right_m, department_m,course_m, video_m, category_m, enrollment_m, Progress_m,
    QuizCheckpoint_m, QuizHistory_m,shift_m, user_shifts_m, shift_change_request_m,shift_roster_m, shift_roster_detail_m,
    attendance_punch_m, attendance_summary_m,leavemaster_m, leavetype_m, leaveconfig_m, leave_balance_m,
    holiday_m, permission_m,salary_structure_m, formula_m, payroll_m, payroll_attendance_m,job_posting_m, job_description_m, candidate_m, candidate_documents_m,
    notification_m, test_report_m,subscription_plans_m
)

# ======================
# IMPORT ROUTERS
# ======================
from app.routes import (
    auth_routes, role_routes, organization_routes, branch_routes,menu_routes, role_right_routes, department_routes,
    categorys_routes, course_routes, video_routes,enrollment_routes, progress_routes,quiz_checkpoint_routes, quiz_history_routes,
    shift_routes, shift_change_request_routes,user_shifts_routes, shift_roster_routes, shift_roster_detail_routes,
    shift_summery_routes,attendance_punch_routes, attendance_summary_routes,leavetype_routes, leave_config_routes, leavemaster_routes, leave_balance_routes,
    holiday_routes, permission_routes,salary_structure_routes, formula_routes,
    payroll_routes, payroll_attendance_routes,job_posting_routes, job_description_routes,
    candidate_routes, candidates_documents_routes,notification_routes, test_report_routes, subscription_plans_routes, module_routes
)

from app.routes.admin_dashboard import user_routes

# ======================
# SEEDERS
# ======================
from app.seeders import run_all_seeders
from app.routes import super_admin_dashboard_routes
from app.routes import subscription_routes


# ======================
# LIFESPAN (STARTUP / SHUTDOWN)
# ======================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup logic
    """
    # ⚠️ Use this ONLY for local/dev.
    # In production → Alembic only.
    Base.metadata.create_all(bind=engine)

    try:
        run_all_seeders()
    except Exception as e:
        print(f"Failed to run seeders on startup: {e}")

    yield

    # Shutdown logic (if needed)


app = FastAPI(
    title="HRMS + LMS Backend",
    lifespan=lifespan
)

# ======================
# CORS MIDDLEWARE
# ======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace "*" with the specific origin of your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======================
# ROOT
# ======================
@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI is running"}


# ======================
# ROUTERS
# ======================
app.include_router(auth_routes.router)
app.include_router(user_routes.router)

app.include_router(role_routes.router)
app.include_router(organization_routes.router)
app.include_router(branch_routes.router)
app.include_router(menu_routes.router)
app.include_router(role_right_routes.router)
app.include_router(department_routes.router)
app.include_router(subscription_plans_routes.router)
app.include_router(subscription_routes.router)
app.include_router(categorys_routes.router)
app.include_router(course_routes.router)
app.include_router(video_routes.router)
app.include_router(enrollment_routes.router)
app.include_router(progress_routes.router)
app.include_router(quiz_checkpoint_routes.router)
app.include_router(quiz_history_routes.router)

app.include_router(job_posting_routes.router)
app.include_router(job_description_routes.router)
app.include_router(candidate_routes.router, prefix="/candidates", tags=["candidates"])
app.include_router(candidates_documents_routes.router)
app.include_router(notification_routes.router)

app.include_router(shift_routes.router)
app.include_router(shift_change_request_routes.router)
app.include_router(user_shifts_routes.router)
app.include_router(shift_roster_routes.router)
app.include_router(shift_roster_detail_routes.router)
app.include_router(shift_summery_routes.router)

app.include_router(attendance_punch_routes.router)
app.include_router(attendance_summary_routes.router)

app.include_router(leavetype_routes.router)
app.include_router(leave_config_routes.router)
app.include_router(leavemaster_routes.router)
app.include_router(leave_balance_routes.router)

app.include_router(holiday_routes.router)
app.include_router(permission_routes.router)

app.include_router(salary_structure_routes.router)
app.include_router(formula_routes.router)
app.include_router(payroll_routes.router)
app.include_router(payroll_attendance_routes.router)

app.include_router(test_report_routes.router)
app.include_router(super_admin_dashboard_routes.router)
app.include_router(module_routes.router)

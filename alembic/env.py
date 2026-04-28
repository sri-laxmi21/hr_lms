import sys
import os
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv

# --------------------------------------------------
# LOAD ENV (DEFAULT = .env → HRM DATABASE)
# --------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

# --------------------------------------------------
# ALEMBIC CONFIG
# --------------------------------------------------
config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

# --------------------------------------------------
# ENSURE APP ROOT IN PATH
# --------------------------------------------------
sys.path.append(BASE_DIR)

# --------------------------------------------------
# IMPORT BASE + MODELS (🔥 REQUIRED FOR AUTOGENERATE)
# --------------------------------------------------
from app.database import Base

from app.models import (
    role_m, user_m, course_m, Progress_m, video_m,
    QuizCheckpoint_m, QuizHistory_m, enrollment_m,
    shift_m, department_m, leavemaster_m, payroll_attendance_m,
    branch_m, category_m, organization_m, salary_structure_m, payroll_m,
    formula_m, permission_m, candidate_documents_m,
    candidate_m, job_posting_m, shift_change_request_m, shift_roster_detail_m,
    user_shifts_m, notification_m, menu_m, role_right_m, shift_roster_m,
    week_day_m, job_description_m, subscription_plans_m, add_on_m,
    organization_add_on_m, payment_m, attendance_punch_m, leavetype_m,
    attendance_summary_m, leaveconfig_m, leave_balance_m, test_report_m,module_m
)

# --------------------------------------------------
# SEEDER RUNNER
# --------------------------------------------------
from app.seeders import run_all_seeders

target_metadata = Base.metadata

# --------------------------------------------------
# DATABASE URL BUILDER
# --------------------------------------------------
def get_database_url():
    db_host = os.getenv("GITHUB_DB_HOST") or os.getenv("DB_HOST")
    return (
        f"mysql+pymysql://{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{db_host}:3306/"
        f"{os.getenv('DB_NAME')}"
    )

# --------------------------------------------------
# OFFLINE MIGRATIONS
# --------------------------------------------------
def run_migrations_offline():
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# --------------------------------------------------
# ONLINE MIGRATIONS + AUTO SEEDING
# --------------------------------------------------
def run_migrations_online():
    connectable = create_engine(
        get_database_url(),
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

    # --------------------------------------------------
    # 🌱 AUTO RUN SEEDERS (CONTROLLED BY ENV FLAG)
    # --------------------------------------------------
    if os.getenv("RUN_SEEDERS", "false").lower() == "true":
        print("🌱 Running seeders after migrations...")
        try:
            run_all_seeders()
            print("✅ Seeders executed successfully")
        except Exception as e:
            print("❌ Seeder execution failed:", e)
            raise

# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
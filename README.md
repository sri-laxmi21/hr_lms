# HR & Learning Management System (HR & LMS)

A comprehensive enterprise-grade platform combining **Human Resource Management (HRMS)** and **Learning Management System (LMS)** functionalities, built with **FastAPI**. This system is designed for multi-tenant environments, providing a scalable solution for organizational growth and employee development.

---

## 🚀 Key Modules

### 🎓 Learning Management System (LMS)
- **Courses & Modules**: Organize content into structured learning paths.
- **Video Learning**: Integrated YouTube video lessons with progress tracking.
- **Quizzes & Assessments**: Evaluate learner knowledge with checkpoints and history.
- **Progress Tracking**: Real-time monitoring of user completion rates.

### 👥 Human Resource Management (HRMS)
- **Employee Management**: Comprehensive user profiles, roles, and branch management.
- **Attendance & Shifts**: Punch-in/out system, automated summaries, and shift roster management.
- **Leave Management**: Configurable leave types, balances, and approval workflows.
- **Payroll**: Attendance-integrated payroll calculation and salary structure management.
- **Recruitment**: Candidate tracking, job postings, and document management.

### 🔐 IAM & Organizations
- **Multi-Tenancy**: Support for multiple organizations with isolated data.
- **RBAC**: Fine-grained Role-Based Access Control and menu permissions.
- **Authentication**: Secure JWT-based auth with OTP verification for admins.
- **Audit Logging**: Comprehensive activity tracking across all modules.

### 💳 Billing & Subscriptions
- **Subscription Plans**: Flexible plan management with module-level access.
- **Payments**: Integrated payment tracking and history.
- **Add-ons**: Scalable organization features with on-demand add-ons.

---

## 📂 tech-stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (Production) / SQLite (Testing)
- **Migrations**: Alembic
- **Auth**: JWT, OTP, Passlib
- **Validation**: Pydantic
- **Tasks**: Background Tasks (Integrated)
- **Storage**: AWS S3 (Helper included)

---

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.9+
- PostgreSQL
- Virtual Environment tool

### Installation
1. **Clone the repo**:
   ```bash
   git clone <repository-url>
   cd hr_lms
   ```

2. **Setup Environment**:
   ```bash
   python -m venv hr_env
   source hr_env/bin/activate  # On Windows: hr_env\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file based on the provided template and set your database and secret keys.

4. **Run Migrations**:
   ```bash
   alembic upgrade head
   ```

5. **Start the Application**:
   ```bash
   uvicorn app.main:app --reload
   ```

---

## 📖 Documentation
Detailed documentation can be found in:
- [Project Overview](PROJECT_OVERVIEW.md)
- [Architecture Deep-Dive](ARCHITECTURE.md)
- [API Reference](app/routes/README.md) (Automated via Redoc/Swagger)
# hr_lms

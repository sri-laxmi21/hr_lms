# Architecture: HR & LMS Technical Design

This document outlines the architectural decisions, data flow, and technical implementation of the HR & LMS platform.

## 🏗️ System Architecture

The application is built on a modern, asynchronous backend architecture using FastAPI. It follows a multi-layered approach to ensure scalability and maintainability.

### 1. Multi-Tenancy Strategy
The system uses a **Table-Level (Shared Schema)** multi-tenancy model.
- Each tenant (Organization) is identified by a unique ID.
- Most tables include an `organization_id` column used to filter data for the specific tenant.
- Middleware or dependency injection is used to enforce organization isolation at the database query level.

### 2. Database Design
- **Engine**: PostgreSQL is used for production for its robust support for relational data and JSON fields.
- **ORM**: SQLAlchemy (Asynchronous) is used for database interactions.
- **Migrations**: Alembic handles schema versioning and deployments.
- **Isolation**: Every transaction is scoped to the current user's organization context.

### 3. Authentication & Security
- **JWT (JSON Web Tokens)**: Used for stateless session management.
- **RBAC**: A comprehensive Role-Based Access Control system is implemented where roles are mapped to specific permissions (e.g., `can_approve_leave`, `can_create_course`).
- **OTP (One-Time Password)**: Integrated for high-security actions, specifically for Organization Admin logins.
- **Encryption**: sensitive data and passwords are hashed using `passlib` with Argon2 or BCrypt.

### 4. Application layers
- **Routes (`app/routes`)**: Handle HTTP requests, input validation via Pydantic, and response formatting.
- **Models (`app/models`)**: SQLAlchemy models representing the database schema.
- **Schema (`app/schema`)**: Pydantic models for request/response validation and serialization.
- **Dependencies (`app/dependencies.py`)**: Reusable logic for auth, database sessions, and organization context.
- **Utilities (`app/utils`)**: Shared helper functions for date manipulation, file handling, and security.

### 5. Infrastructure & Storage
- **File Storage**: AWS S3 (or S3-compatible storage) is used for resumes, profile pictures, and lesson documents.
- **Media Delivery**: YouTube is used as the primary video delivery network, reducing server bandwidth and storage costs.
- **Logging**: Integrated logging for application errors and a dedicated **Audit Log** system for tracking business-critical actions.

## 🔄 Core Workflows

### Request Lifecycle
1. Client sends request with JWT.
2. `AuthDependency` validates JWT and extracts user/org context.
3. `PermissionDependency` checks if the user has the required permission for the route.
4. Route handler processes logic, interacting with the database via `session`.
5. Pydantic schema validates the response before sending it back to the client.

### Background Tasks
Lightweight background tasks are used for non-blocking operations:
- Sending emails/SMS.
- Generating attendance summaries.
- Updating user progress metrics.

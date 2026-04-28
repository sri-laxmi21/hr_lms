# Project Overview: HR & LMS

This document provides a detailed breakdown of the features and functionalities available in the HR & Learning Management System.

## 🎓 Learning Management System (LMS)

The LMS module is designed to provide users with a seamless learning experience, primarily through video-based content.

- **Course Management**: Admins can create and manage courses, categorical tagging, and descriptions.
- **Module Structure**: Courses are broken down into logical modules, each containing one or more videos.
- **Video Player**: Integrated YouTube player for lesson delivery.
- **Progress Tracking**: Tracks which videos a user has watched and calculates overall course completion percentage.
- **Assessments**:
    - **Quiz Checkpoints**: Periodic knowledge checks within modules.
    - **Quiz History**: Detailed logs of user performance in various tests.

## 👥 Human Resource Management (HRMS)

The HRMS module handles all employee lifecycle and organizational management tasks.

- **Organization & Branch**: Support for nested organizational structures and multiple physical branches.
- **Department & Role**: Define departmental silos and specific job roles with associated permissions.
- **Attendance System**:
    - **Punching**: Daily clock-in/out tracking.
    - **Attendance Summary**: Aggregated daily and monthly attendance reports.
    - **Payroll Integration**: Attendance data automatically feeds into the payroll engine.
- **Leave Management**:
    - **Leave Types**: Support for Casual, Sick, Earned, and other custom leave types.
    - **Balance Tracking**: Automated accrual and deduction of leave balances.
    - **Approval Workflow**: Multi-stage leave request and approval process.
- **Shift Management**:
    - **Shift Definition**: Configurable shift timings (morning, evening, night).
    - **Roster Management**: Assign shifts to users and manage roster changes.
- **Recruitment (ATS)**:
    - **Job Postings**: Manage internal and external job openings.
    - **Candidate Tracking**: Track applicants through various stages.
    - **Document Management**: Store and verify candidate resumes and identity documents.

## 🔐 Identity & Access Management (IAM)

Security and access control are central to the system.

- **User Profiles**: Detailed employee profiles including personal, professional, and bank details.
- **RBAC (Role-Based Access Control)**:
    - **Permissions**: Granular control over every API endpoint.
    - **Menu Rights**: Dynamic UI sidebar rendering based on user roles and permissions.
- **Multi-Tenancy**: Complete data isolation between different organizations sharing the same infrastructure.
- **Audit Logs**: Logs every critical action (Create, Update, Delete) for security and compliance.

## 💳 Billing & Subscriptions

Manages the monetization and feature access for client organizations.

- **Subscription Plans**: Define plans with different feature sets (modules).
- **Organization Subscriptions**: Tracks which plan an organization is currently on and its expiry.
- **Add-ons**: Purchase additional features without upgrading the entire plan.
- **Payments**: Detailed log of all subscription-related transactions.

## 🔔 Notifications & Communication

- **System Notifications**: In-app notifications for important events (leave approval, course enrollment).
- **Email/SMS Integration**: Support for external communication for OTP and critical alerts.

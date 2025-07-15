# FinDash – Beginner-Focused Financial Dashboard

**FinDash** is a secure and beginner-friendly financial dashboard built with Django.  
It helps users visualize and manage their finances by linking bank accounts (via Plaid), viewing transactions, tracking budgets, and monitoring account growth over time.

---

## 📌 Project Goals

- Provide a simple, trustworthy interface for new users to understand their finances
- Encourage healthy financial habits and education
- Support account linking, budgeting, and clear financial summaries

---

## ✅ Current Features

- Custom Django user authentication
- Plaid sandbox integration for account linking
- Account, transaction, and budget views with clean UI
- Secure token storage and account summaries

---

## 🔄 Upcoming Features

Starting **July 14, 2025**, the codebase will follow a consistent, professional workflow, including:

- [ ] Monthly account % change tracking
- [ ] Dashboard page with financial summary widgets
- [ ] Redesigned settings page with user preferences
- [ ] Notification system and optional 2FA
- [ ] Organized GitHub tickets with Epics and sprint-based planning

---

## 🧠 Tech Stack

- Python / Django
- SQLite (development), PostgreSQL (production)
- Tailwind CSS (frontend)
- Plaid API (sandbox mode)

---

## 📁 Project Structure
.github/ # GitHub Actions workflows
config/ # Django project settings (urls, settings, wsgi, asgi)
core/ # Main app: models, views, migrations, business logic
plaid_link/ # Plaid API integration (Link token, account sync)
users/ # Custom user model and authentication
templates/ # HTML templates for all views
static/ # CSS and icons
manage.py # Django management script
requirements.txt # Python dependencies

---

## 💬 Notes

> This project began as a learning experiment and has now transitioned into a polished, professional codebase as of **July 14, 2025**.  
> All code, tickets, and commits going forward will reflect this shift in quality and consistency.
> Git history was rebased July 15th, 2025 to unify authorship (accidental secondary Git identity). Feature branches and PR workflow were consistently used.

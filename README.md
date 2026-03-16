# Web101 - Basic Flask Auth Demo

## Features
- Register
- Login / Logout
- Role-based access (`user`, `admin`)
- Admin page to list users

## Quick Start
1. Create virtual env (optional):
   - Windows PowerShell: `python -m venv .venv; .\.venv\Scripts\Activate.ps1`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Run app:
   - `python app.py`
4. Open:
   - `http://127.0.0.1:5000`

## Notes
- Route `/bootstrap-admin` creates default admin account `admin/admin123` for local testing.
- Do not use this setup as-is in production.

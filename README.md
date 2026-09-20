# Card Management Web

Beginner-friendly Card Management Web project using Flask, SQLite, HTML, CSS, JavaScript and Docker.

## Run in VS Code

```powershell
cd C:\Users\DELL\OneDrive\Desktop\card-management-web
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python backend\app.py
```

Open http://localhost:5010

If activation is blocked:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## Docker

```powershell
docker compose up --build
```

Open http://localhost:5010

## Structure

```text
card-management-web/
├── backend/app.py
├── backend/requirements.txt
├── frontend/index.html
├── frontend/style.css
├── frontend/script.js
├── Dockerfile
├── docker-compose.yml
└── README.md
```

For learning/portfolio use. Do not use this demo as a production system for real payment-card data.

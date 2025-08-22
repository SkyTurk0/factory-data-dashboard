# Factory Data Dashboard

## 📌 Overview

This project is a **full-stack Factory Data Dashboard MVP** built with **Flask** (backend API) and **React + Vite** (frontend). It demonstrates a real-world industrial automation use case: monitoring factory machines, visualizing logs, and enabling digitalization in manufacturing environments.

The system simulates a small set of machines and their operational logs. The frontend consumes API endpoints from the backend and displays data in a responsive dashboard.

---

## 🚀 Features

- **Flask REST API** providing machine and log data
- **React + Vite frontend** for visualization
- Real-time factory simulation data (extendable)
- Modular structure: `backend/` and `frontend/`
- Ready for extension with authentication, charts, or database integration

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Frontend**: React, Vite, Fetch API
- **Version Control**: Git & GitHub
- **Optional Extensions**: SQLite/PostgreSQL, Docker, CI/CD

---

## 📂 Project Structure

```
factory-data-dashboard/
│
├── backend/                # Flask API backend
│   ├── app.py               # Flask routes
│   ├── requirements.txt     # Python dependencies
│   └── ...
│
├── frontend/               # React + Vite frontend
│   ├── src/                 # React components
│   ├── package.json         # Node dependencies
│   └── ...
│
├── .gitignore
├── README.md
└── LICENSE
```

---

## ⚡ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/SkyTurk0/factory-data-dashboard.git
cd factory-data-dashboard
```

### 2. Run the backend (Flask)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # (Windows)
pip install -r requirements.txt
python app.py
```

Backend will start on: [**http://127.0.0.1:5000**](http://127.0.0.1:5000)

Example endpoints:

- `GET /machines`
- `GET /logs/<id>`

### 3. Run the frontend (React + Vite)

```bash
cd ../frontend
npm install
npm run dev
```

Frontend will start on: [**http://localhost:5173**](http://localhost:5173)

---

## 📊 Example Output

**Machines Endpoint:**

```json
[
  {"id": 1, "name": "Packaging Unit", "status": "Running"},
  {"id": 2, "name": "CNC Machine", "status": "Idle"},
  {"id": 3, "name": "Assembly Robot", "status": "Running"}
]
```

---

## 💡 Future Improvements

- Database integration (PostgreSQL/SQLite)
- Real-time updates (WebSockets)
- Role-based authentication
- Data visualization with charts (Plotly/Recharts)
- Dockerized deployment
- CI/CD pipeline

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 👤 Author

- **Your Name**\
  📧 [soylemez.yusuf01@gmail.com](mailto\:soylemez.yusuf01@gmail.com)\
  🔗 [LinkedIn](https://www.linkedin.com/in/yusuf-ahmet-s%C3%B6ylemez-ab32981a9/) | [GitHub](https://github.com/SkyTurk0)

---

> This project was developed as part of a professional portfolio to demonstrate full-stack engineering skills in industrial automation and software development.


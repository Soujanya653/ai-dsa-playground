# AI-Flavored Practice Planner (Team B)

## 📌 Project Overview

This project is a personalized practice planner for LeetCode-style problems.
It generates a daily study plan based on available time, difficulty range,
and adapts problem difficulty using user feedback.

The system is built using Python, FastAPI, and Streamlit with clean modular design
and unit-tested core logic.

---

## 🏗️ Architecture

- Frontend: Streamlit UI
- Backend: FastAPI REST APIs
- Core Logic: Heap-based scheduler and difficulty adapter
- Storage: JSON files

---

## ⚙️ Technology Stack

- Python 3.x
- FastAPI
- Streamlit
- Pytest
- Black, isort, Ruff
- Git & GitHub

---

## ▶️ How to Run the Project

### 1️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
2️⃣ Run Backend
cd backend
uvicorn app.main:app --reload
Backend runs at: http://localhost:8000

3️⃣ Run Frontend
Open new terminal:

cd frontend
streamlit run app.py
Frontend runs at: http://localhost:8501

🧪 How to Run Tests
From team-b-planner folder: 
python -m pytest

🧹 Code Quality Tools
Format code:

black .
isort .
Run linter:

ruff check .
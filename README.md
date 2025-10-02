# Lab 4 — Tkinter & PyQt Integration
**Authors:** Georges Bassil & Philippe Doumet  
**Course:** EECE 435L

---

## 📖 Project Overview
This project demonstrates two different GUI frameworks in Python, both connected to a common backend/database:

- **Tkinter UI** (Georges): A simple desktop interface built with Tkinter.  
- **PyQt UI** (Philippe): A desktop interface built with PyQt.  

Both interfaces rely on shared backend logic (`db.py`, `Person.py`, `Student.py`, `Instructor.py`, `Course.py`) to manage students and courses.

---

## 🗂 Repository Structure
Lab4-Project/
│
├── Course.py # Course class
├── Instructor.py # Instructor class
├── Person.py # Person base class
├── Student.py # Student class
├── db.py # Database logic
├── main_window_Tkinter_db.py # Tkinter interface
├── main_window_PyQt_db.py # PyQt interface
├── README.md # Project documentation
└── venv/ # Local virtual environment (ignored in git)


## ⚙️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/georges004/Lab4-GeorgesBassil_PhilippeDoumet.git
   cd Lab4-GeorgesBassil_PhilippeDoumet
Create and activate a virtual environment

macOS/Linux:

python3 -m venv .venv
source .venv/bin/activate

Windows:
python -m venv .venv
.venv\Scripts\activate
Install dependencies
pip install -r requirements.txt
(Tkinter is included with Python, only PyQt needs installation separately if required):

pip install PyQt6
▶️ Running the Applications
Run Tkinter UI
python main_window_Tkinter_db.py
Opens a simple window for adding students and courses.

Uses db.py to persist data.

Run PyQt UI

python main_window_PyQt_db.py
Opens a PyQt-based interface with similar functionality.

Also connects to the same backend.

✅ Features
Shared backend (db.py) to ensure consistency.

Two UIs (Tkinter & PyQt) demonstrating different frameworks.

Student/course management: add students to courses through either interface.

Error handling for empty/invalid input.

🔄 Workflow (Git & Collaboration)
Each student worked on a separate branch (feature-tkinter-ui, feature-pyqt-ui).

Changes were merged into main via Pull Requests.

Final version is tagged as v1.0.

🏷 Final Release
To check the tagged release on GitHub:

Go to the Releases section.

Download the latest packaged version.

📌 Notes
Both UIs are independent — you can run either Tkinter or PyQt.

Future work: add a launcher script (run.py) to choose between UIs with one command.








# FamilyCare AI 🌸
### *Smart Elderly Care & Family Coordination Platform*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36%2B-FF4B4B.svg)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gen%20AI-Gemini%202.5%20Flash-8E75C2.svg)](https://aistudio.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-teal.svg)](LICENSE)

**FamilyCare AI** is a Python-focused, AI-powered healthcare coordination platform engineered to help adult children care for aging parents when family members live in different cities.

---

## 🌟 The Problem & The Solution

- **The Challenge**: Millions of families are geographically separated. An aging parent lives in Chicago, while their children live in New York and Seattle. Daily phone calls get missed, siblings constantly wonder *"Did Mom take her heart medication?"* or *"Who is driving Mom to cardiology next Tuesday?"*, and caregiver burnout accelerates.
- **The Solution**: A unified family operating system with **one-tap morning check-ins ("I'm Okay")**, **medication adherence tracking**, **coordinated doctor appointments**, **shared family errands**, and **Google Gemini AI intelligence** that synthesizes weekly care reports with strict privacy safeguards.

---

## 🚀 Key Platform Features

| Capability | Description | Technologies |
| :--- | :--- | :--- |
| **3D Care Scene** | Interactive WebGL scene featuring floating 3D pills, heartbeat mesh, and multi-city connection orbits (Chicago, NYC, Seattle). | Three.js & HTML5 Canvas |
| **Morning Check-In** | One-tap *"I'm Okay"* routine with configurable target times (09:00 AM) and grace periods (60 mins). Detects missed check-ins without panicking families. | Python `datetime`, SQLite |
| **Medication Tracking** | Schedules recurring doses, records user acknowledgements, and strictly distinguishes recorded acknowledgements from verified clinical consumption. | SQLAlchemy ORM |
| **Appointments & Tasks** | Coordinate specialist consultations, assigned family companions, transit logistics, and shared household errands. | SQLite, Python Datetime |
| **Google Gemini AI** | Privacy-conscious weekly care digests, doctor visit prep checklists, and cross-city sibling duty division using the official `google-genai` SDK. | Google Gen AI SDK |
| **Plotly 3D Analytics** | Interactive 3D visual landscape (Day of Week vs Check-In Hour vs Punctuality Variance) and adherence trends. | Pandas, NumPy, Plotly |
| **Experimental ML** | Transparent rule-based safety baseline paired with an experimental Scikit-Learn **Isolation Forest** model to detect routine anomalies. | Scikit-Learn |

---

## 🏗️ System Architecture

```
familycare-ai/
├── app.py                      # Modern multi-page navigation (st.navigation)
├── config.py                   # App configuration, palette tokens, secrets loader
├── git_ops.py                  # Portable Git operations and commit logging (Dulwich)
│
├── database/
│   ├── connection.py           # SQLite engine & SQLAlchemy scoped sessions
│   ├── models.py               # 9 Relational entities (Users, Families, Members, Logs, etc.)
│   └── seed_data.py            # Fictional multi-city demo scenario generator (Vance Family)
│
├── services/
│   ├── member_service.py       # Distributed family member CRUD & caregiver assignment
│   ├── checkin_service.py      # Grace periods, 'I'm Okay' logger, missed check-in detection
│   ├── medication_service.py   # Medication schedules, acknowledge logs, adherence tracking
│   ├── appointment_service.py  # Doctor visits, clinic details, companion escorts
│   ├── task_service.py         # Shared family tasks, grocery runs, prescription refills
│   ├── notification_service.py # In-app notification center & simulation alerts
│   └── gemini_service.py       # Google Gen AI Python SDK, Pandas privacy pre-processing
│
├── analytics/
│   ├── data_processor.py       # Pandas/NumPy aggregations & completion metrics
│   └── visualizations.py       # Plotly 2D charts & 3D activity landscapes
│
├── ml/
│   └── activity_pattern.py     # Rule baseline + Scikit-Learn Isolation Forest
│
├── components/
│   ├── ui_helpers.py           # Healthcare glassmorphism cards, badges, and banners
│   └── three_scene.py          # Interactive Three.js WebGL 3D care scene with SVG fallback
│
├── pages/                      # 10 Dedicated Streamlit pages
│   ├── 1_Home.py
│   ├── 2_Family_Dashboard.py
│   ├── 3_Family_Members.py
│   ├── 4_Daily_CheckIns.py
│   ├── 5_Medication_Reminders.py
│   ├── 6_Appointments.py
│   ├── 7_Care_Tasks.py
│   ├── 8_AI_Care_Companion.py
│   ├── 9_Data_Analytics.py
│   └── 10_About_and_Privacy.py
│
├── assets/custom.css           # Premium glassmorphic styling, animations, colors
└── tests/test_services.py      # Automated unit test suite (9 tests passing)
```

---

## 🛠️ Installation & Quickstart

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- Recommended: Virtual environment (`venv` or `conda`)

### Step 1: Clone or Navigate to the Repository
```bash
git clone https://github.com/your-username/familycare-ai.git
cd familycare-ai
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables (Optional for AI)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your Google Gemini API key from [Google AI Studio](https://aistudio.google.com/):
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
> **Note**: All core application features (Check-Ins, Medication Reminders, Appointments, Tasks, 3D Visualizations, and Analytics) run **100% locally with zero API key requirement**. The API key is only needed when synthesizing real-time Gemini summaries.

### Step 4: Launch the Streamlit Application
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 🧪 Running Automated Unit Tests

Execute the comprehensive test suite verifying the database, services, analytics processor, and ML models:
```bash
python tests/test_services.py
```
Expected output:
```
Ran 9 tests in 0.346s
OK
```

---

## 🧑‍⚖️ Hackathon Judge Evaluation Guide

Follow this 5-minute walkthrough to evaluate all features:

1. **Landing Page (`Home`)**:
   - Inspect the interactive **Three.js 3D WebGL scene** (click and drag to rotate the orbital nodes linking Chicago, New York, and Seattle).
   - Review the problem/solution breakdown and multi-city case study.

2. **Family Dashboard**:
   - Inspect live KPIs queried directly from SQLite (Family Members, Check-In Status, Medication Reminders, Upcoming Appointments).
   - Use the **Judge Control Center** expander to click `Reload Demo Data` to test the pre-seeded Vance Family dataset.

3. **Daily Check-Ins**:
   - View today's status for Eleanor Vance.
   - Click the green **"I'm Okay! (Tap to Check In)"** button with a mood selection. Observe immediate status update and notifications.
   - Click **"Trigger Simulated Overdue Check-In"** to observe simulated escalation workflows.

4. **Medications & Appointments**:
   - Acknowledge a morning Lisinopril medication dose.
   - Review scheduled cardiology appointment with Dr. Ramirez and see companion escort logistics.

5. **AI Care Companion**:
   - Enter your Gemini API key in the settings expander (or set `GEMINI_API_KEY` in `.env`).
   - Click **"✨ Generate Weekly Care Summary"** to observe privacy-conscious data pre-processing and structured Gemini synthesis.
   - Try the quick prompt chips (e.g. *"Doctor Visit Prep Checklist"*).

6. **Data Analytics & 3D**:
   - Interact with the **3D Morning Routine Landscape** (Plotly 3D WebGL scatter). Rotate in 3D to evaluate morning check-in stability.
   - Inspect 30-day compliance curves, medication adherence bars, and task category donuts.

7. **About & Privacy**:
   - Review the **Scikit-Learn Isolation Forest** experimental activity analysis, feature explanations, and ethical medical disclaimers.

---

## 🛡️ Privacy, Security & Medical Disclaimers

1. **Data Minimization**: FamilyCare AI collects only essential scheduling and contact parameters. No health insurance identifiers, SSNs, financial information, or EHR records are stored.
2. **Privacy-Preserving AI**: Before dispatching prompts to the Gemini API, our Pandas pre-processing pipeline strips personal addresses, names, and contact numbers, transmitting only aggregated non-PII metrics.
3. **Medical Disclaimer**:
   > **IMPORTANT**: FamilyCare AI is designed strictly for family coordination, routine tracking, and administrative scheduling. It is **NOT** a certified medical device, emergency dispatch system, or diagnostic tool. A missed check-in does **NOT** automatically constitute a medical emergency. In urgent health situations, always dial local emergency services (e.g. 911).

---

## 📜 License
Distributed under the MIT License. Built with ❤️ for families everywhere during the Healthcare AI Hackathon.

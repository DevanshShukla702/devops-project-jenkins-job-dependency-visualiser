# FlowTrace: Jenkins Job Dependency Visualiser

**Student Name:** Devansh Shukla  
**Registration No:** 23FE10CSE00741  
**Course:** CSE3253 DevOps [PE6]  
**Semester:** VI (2025–2026)  
**Project Type:** Jenkins & CI  
**Difficulty:** Advanced  

---

## 📌 Project Overview

FlowTrace transforms from a basic academic tool into a **professional, production-grade DevOps visualization platform**. It provides interactive graphs, dependency tracing, robust metrics, and an immersive UI built for modern SRE and DevOps workflows.

![FlowTrace Dashboard Screenshot](https://via.placeholder.com/800x400.png?text=FlowTrace+Dashboard+-+Real-time+Jenkins+Visualization)

---

## 🚀 Key Features

* **Real-Time Node Graph:** An interactive, smooth-panning vis-network graph displaying entire CI/CD environments.
* **Deep Dependency Tracing:** Clear visual mapping of upstream vs downstream jobs.
* **Live Status Updates & Auto-Refresh:** Constant synchronisation directly from the Jenkins REST APIs.
* **Modern Premium UI/UX:** Complete dark-mode interface, glassmorphism panels, GSAP page transitions, and toast notifications.
* **Intelligent Metrics Dashboard:** Job counts, success rates, and active states parsed instantly.
* **Built-in Authentication:** Protect your infrastructure data utilizing Flask-Login sessions.
* **Demo Mode Support:** Includes a robust offline data mocking engine for portfolio showcases without needing an active Jenkins server.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.11, Flask, Flask-Login, SQLite
- **Frontend:** HTML5, CSS3, Vanilla JS, GSAP, tsParticles, vis-network
- **Data Integrations:** Jenkins REST API

---

## 📂 Project Structure

```text
src/main/python/
├── api/
│   ├── app.py                  # Main Flask App & Routing
│   ├── static/                 # CSS/JS Assets (glassmorphism/GSAP/particles)
│   └── templates/              # HTML layout (Dashboard, Landing, Auth)
├── config/
│   ├── config.yaml             # Settings (Auth, API credentials)
│   └── mock_data.json          # Demo Mode static offline data
├── models/
│   └── user.py                 # SQLite backed User ORM
├── services/
│   ├── jenkins_service.py      # Live external parsing
│   ├── mock_service.py         # Testing parsing logic
└── visualization/
    └── graph_builder.py        # Mapping algorithms for Graph layouts
```

---

## ▶️ Setup Guide & How to Run

### 1. Requirements & Installations
Provide a virtual environment, then install dependencies:
```bash
python -m venv .venv
# Activate
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

pip install flask flask-login requests pyyaml werkzeug
```

### 2. Configure Settings
Copy `config.yaml` guidelines and adapt your token. To quickly test UI, enable `demo_mode: true` to bypass networking constraints.

### 3. Start the Platform
```bash
python src/main/python/api/app.py
```

### 4. Open in Browser
Visit the live local instance at:
[http://localhost:5000](http://localhost:5000)

*Log in through Demo Bypass or create an admin account.*

---

## 📸 Interactive Tour

* **Landing Page:** Interactive particle mesh welcoming new users.
* **Jobs Table:** Sortable and exportable CSV listings of the current build footprint.
* **Visual Graph:** Live node-links showcasing exact execution traces.

---

## ✅ Continuous Evolution

FlowTrace continues to evolve. Follow future developments regarding real-time webhooks, alerting interfaces, and expanded multi-cluster mappings!
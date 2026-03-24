# FlowTrace: Operational Intelligence & Dependency Visualizer

---

## 📌 Platform Overview

**FlowTrace** is a professional, production-grade DevOps visualization platform engineered to bridge the gap between raw functional automation and clear operational intelligence. It transforms standard Jenkins pipelines from text logs into fully interactive, auto-updating dependency graphs. 

Designed for large-scale CI/CD environments, FlowTrace eliminates the complexity of tracing upstreams, downstreams, and build failures by providing a unified, real-time visual interface.

<div align="center">
  <img src="https://via.placeholder.com/800x400.png?text=FlowTrace+Dashboard+-+Real-time+Jenkins+Visualization" alt="FlowTrace Dashboard">
</div>

---

## 🚀 Key Platform Features

* **Real-Time Node Graphing:** Translates complex CI/CD relationships into smooth, top-down vis-network maps that instantly highlight execution traces.
* **Intelligent Metrics Dashboard:** Job counts, success rates, and live active states parsed natively from REST API payloads.
* **Deep Dependency Tracing:** Clear, interactive visual routing of multi-tiered upstream/downstream jobs.
* **Modern Premium UI/UX:** Complete dark-mode interface, glassmorphism panels, GSAP page transitions, and toast event notifications.
* **Robust Data Mocking Engine:** Includes a robust offline simulated-pipeline state engine designed for disconnected testing and portfolio demonstration.
* **Secure Authorization:** Protects infrastructure data utilizing session-backed Flask-Login configurations.

---

## 🛠️ Technology Stack

**Backend & Data Services:**
* Python 3.11, Flask
* SQLite, Flask-Login, Werkzeug
* Jenkins REST API & Custom Polling Service

**Frontend & Visuals:**
* HTML5, CSS3, Vanilla JS
* Data Visualization: `vis-network`
* CSS Interactions: `tsParticles`, `GSAP` animations

---

## 📂 Architecture & Project Structure

The repository follows a clean, enterprise-ready structure separating infrastructure configuration from the web API source code:

```text
├── deliverables/           # Compiled builds and release notes
├── docs/                   # Architectural documentation & API references
├── infrastructure/         # IaC, deployment scripts, and provisioning assets
├── monitoring/             # System health configurations (Grafana/Prometheus logic)
├── pipelines/              # Core Jenkinsfile definitions and shared libraries
├── presentations/          # Technical slide decks and product overviews
├── requirements.txt        # Python dependency manifest
├── tests/                  # Unit tests and automated integration checks
└── src/
    └── main/
        └── python/
            ├── api/                  # Main Flask App & Routing
            │   ├── static/           # Global design system (CSS/JS)
            │   └── templates/        # Dashboard, Landing, and Auth layouts
            ├── config/               # Settings (API credentials, Mock State Data)
            ├── models/               # SQLite-backed ORM definitions
            ├── services/             # Jenkins API ingestion & caching layers
            └── visualization/        # Top-down graph mathematical build logic
```

---

## ▶️ Setup Guide & Local Deployment

### 1. Requirements & Bootstrapping
Activate a clean virtual environment and install the required dependencies:
```bash
python -m venv .venv

# Activate the environment
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configuration Settings
Define your connection target in `src/main/python/config/config.yaml`.
* To pull real telemetry, supply your Jenkins URI and token. 
* To test the UI logic offline (mock analytics), enable `demo_mode: true`.

### 3. Start the Data Integration Server
Initialize the Python visualization microservice:
```bash
python src/main/python/api/app.py
```

### 4. Connect to Interface
Visit the live local instance at:
**[http://localhost:5000](http://localhost:5000)**

*Log in through the Demo Bypass on the Welcome screen, or register an administrative root account to interact with the map.*

---

## ✅ Continuous Evolution Roadmap

FlowTrace is designed with future extensions in mind:
- **v1.1 Metrics Hub:** Introducing advanced historical charting (`Chart.js`) and build-time deviation analysis.
- **v1.2 Real-time Webhooks:** Upgrading the Jenkins polling layer to pure WebSocket pushes for sub-second GUI latency.
- **v2.0 Multi-Server Aggregation:** Creating unified pipeline views synced across entirely separate Jenkins clusters.
# FlowTrace
> Real-Time Operational Intelligence & Pipeline Dependency Visualizer

## Overview
FlowTrace is a production-grade DevOps visualization platform engineered to bridge the gap between raw functional automation and operational intelligence. It transforms standard Jenkins pipelines from text logs into fully interactive, auto-updating dependency graphs, allowing engineering teams to instantly trace upstreams, downstreams, and build failures.

## Key Features
* **Real-Time DAG Visualization:** Translates complex CI/CD relationships into directed acyclic graphs (DAG) that highlight execution traces.
* **Intelligent Telemetry Dashboard:** Parses job counts, success rates, and live active states natively from REST API payloads.
* **Dual-Mode Engine:** Includes a robust mock-state engine designed for disconnected testing and portfolio demonstrations without needing a live Jenkins instance.
* **Secure Access Control:** Session-backed authentication using Flask-Login and Werkzeug security.

## Tech Stack
* **Backend:** Python 3.11, Flask, SQLAlchemy, Flask-Limiter
* **Database:** SQLite (Local) / Supabase PostgreSQL (Production)
* **Frontend:** HTML5, CSS3, Vanilla JS, `vis-network` (Graphing), GSAP (Animations)
* **Integrations:** Jenkins REST API 

## Architecture & Data Flow
FlowTrace utilizes a modular monolithic architecture. The frontend consumes REST endpoints exposed by the Flask API. The backend features an abstraction layer (`JenkinsClient`) that uses TCP connection pooling to efficiently fetch and parse thousands of Jenkins jobs. A mathematical transformation layer (`graph_builder.py`) resolves these dependencies into nodes and edges before serving them to the client.

## Engineering Decisions
* **TCP Connection Pooling:** Utilizing `requests.Session()` in the Jenkins client minimizes latency and prevents port exhaustion during heavy API polling.
* **Service Abstraction Layer:** The backend dynamically injects either a live Jenkins client or a Mock Service based on environment variables, enabling seamless local development.
* **O(N+E) Graph Parsing:** The graph builder parses upstreams and downstreams in a single pass to ensure O(N+E) time complexity, critical for scaling to large Jenkins clusters.

## Challenges & Solutions
**Challenge:** Managing high-latency cold starts with the Supabase PostgreSQL database caused intermittent 500 errors on the initial dashboard load.
**Solution:** Engineered a custom `_query_with_retry` wrapper in the SQLAlchemy data models that catches `OperationalError` exceptions, initiates a graceful backoff, and automatically retries the query, ensuring a stable user experience.

## Setup Instructions
```bash
# 1. Clone & create virtual environment
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure Environment (Optional: set FLOWTRACE_DEMO_MODE=true)
cp .env.example .env

# 4. Start Server
set PYTHONPATH=src
python src/api/app.py
```

## Future Improvements
- **WebSocket Integration:** Transition from REST polling to pure WebSocket pushes for sub-second GUI latency.
- **Multi-Cluster Aggregation:** Create unified pipeline views synced across entirely separate Jenkins clusters.
# FlowTrace: Jenkins Job Dependency Visualiser

**Student Name:** Devansh Shukla  
**Registration No:** 23FE10CSE00741  
**Course:** CSE3253 DevOps [PE6]  
**Semester:** VI (2025–2026)  
**Project Type:** Jenkins & CI  
**Difficulty:** Intermediate  

---

## 📌 Project Overview

FlowTrace is a DevOps visualization tool that provides a clear and interactive representation of Jenkins job dependencies. It helps users understand CI/CD pipelines by displaying jobs, their execution flow, and relationships in a structured graph format.

---

## 🚀 Key Features

- Visual representation of Jenkins job dependencies  
- Top-to-bottom pipeline flow visualization  
- Status-based node coloring (Success, Failed, Unstable, Not Built)  
- Interactive graph (click nodes to view details)  
- Upstream and downstream job tracking  
- Real-time data fetched from Jenkins REST API  
- Clean and modern UI for better readability  

---

## 🛠️ Tech Stack

- Backend: Python 3.11, Flask  
- Frontend: HTML5, CSS3, JavaScript (Vanilla)  
- Visualization: vis-network  
- Configuration: YAML  
- API Integration: Jenkins REST API  

---

## 📂 Project Structure

src/main/python/

- api/
  - static/
    - graph.js
    - style.css
  - templates/
    - dashboard.html
  - app.py

- services/
  - jenkins_service.py

- visualization/
  - graph_builder.py

- config/
  - config.yaml

---

## ⚙️ How It Works

1. Jenkins jobs are fetched using Jenkins REST API  
2. Backend processes job data and builds dependency graph  
3. API (/api/graph) returns structured JSON  
4. Frontend fetches data and renders graph using vis-network  
5. Users interact with nodes to view job details  

---

## ▶️ How to Run

### Activate virtual environment
Windows:
.venv\Scripts\activate  

Linux/Mac:
source .venv/bin/activate  

### Install dependencies
pip install -r requirements.txt  

### Run application
python src/main/python/api/app.py  

### Open in browser
http://localhost:5000  

---

## 📸 Output

- Interactive dependency graph  
- Job status visualization  
- Detailed job information panel  

---

## 🎯 Use Case

- Helps DevOps engineers understand CI/CD pipelines  
- Useful for debugging pipeline flow  
- Improves visibility of job dependencies  

---

## 📌 Future Enhancements

- Metrics dashboard (success rate, build trends)  
- Real-time auto-refresh  
- Multi-project support  

---

## ✅ Conclusion

FlowTrace simplifies Jenkins pipeline visualization by converting complex job dependencies into an intuitive graphical interface, improving debugging, monitoring, and understanding of CI/CD workflows.
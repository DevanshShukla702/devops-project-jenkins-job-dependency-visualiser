from flask import Flask, jsonify, render_template
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.jenkins_service import get_all_jobs, get_job_details
from visualization.graph_builder import build_graph

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/graph")
def graph():
    try:
        jobs = get_all_jobs()
        jobs_data = []

        for job in jobs:
            name = job["name"]
            details = get_job_details(name)

            jobs_data.append({
                "name": name,
                "details": details
            })

        return jsonify(build_graph(jobs_data))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
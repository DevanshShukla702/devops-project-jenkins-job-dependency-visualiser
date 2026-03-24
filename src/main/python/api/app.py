import sys
import os
import yaml
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.user import User
from visualization.graph_builder import build_graph
import services.jenkins_service as jenkins_service
import services.mock_service as mock_service

# Load Config
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml"))
with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

app_config = config.get("app", {})
DEMO_MODE = app_config.get("demo_mode", False)
AUTH_ENABLED = config.get("auth", {}).get("enabled", False)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = config.get("auth", {}).get("secret_key", "dev-fallback-key")

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

def get_service():
    if DEMO_MODE:
        return mock_service
    return jenkins_service

@app.route("/")
def index():
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if not AUTH_ENABLED:
        return redirect(url_for("dashboard"))
        
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        demo_bypass = request.form.get("demo_bypass")
        
        if demo_bypass == "true":
            # Automatically find or create demo user
            demo_user = User.find_by_username("demo")
            if not demo_user:
                User.create("Demo User", "demo@flowtrace.local", "demo", "demo")
                demo_user = User.find_by_username("demo")
            login_user(demo_user)
            return redirect(url_for("dashboard"))
            
        user = User.find_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid username or password", "error")
        
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if not AUTH_ENABLED:
        return redirect(url_for("dashboard"))
        
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        
        if password != confirm:
            flash("Passwords do not match", "error")
            return redirect(url_for("register"))
            
        if User.create(name, email, username, password):
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Username or email already exists", "error")
            
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required if AUTH_ENABLED else lambda x: x
def dashboard():
    return render_template("dashboard.html", user=current_user if not current_user.is_anonymous else None)

@app.route("/jobs")
@login_required if AUTH_ENABLED else lambda x: x
def jobs_page():
    return render_template("jobs.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/jenkins-guide")
def guide():
    return render_template("guide.html")

# ========== API ROUTES ==========

@app.route("/api/graph")
@login_required if AUTH_ENABLED else lambda x: x
def graph():
    try:
        service = get_service()
        jobs = service.get_all_jobs()
        jobs_data = []

        for job in jobs:
            name = job["name"]
            details = service.get_job_details(name)
            jobs_data.append({
                "name": name,
                "color": job.get("color", "notbuilt"),
                "details": details
            })

        return jsonify(build_graph(jobs_data))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/jobs")
@login_required if AUTH_ENABLED else lambda x: x
def api_jobs():
    try:
        service = get_service()
        jobs = service.get_all_jobs()
        
        jobs_detail_list = []
        for job in jobs:
            name = job["name"]
            details = service.get_job_details(name)
            last_build = details.get("lastBuild", {}) or {}
            jobs_detail_list.append({
                "name": name,
                "color": job.get("color", "notbuilt"),
                "build_number": last_build.get("number"),
                "duration": last_build.get("duration"),
                "upstream": [u.get("name") for u in details.get("upstreamProjects", [])],
                "downstream": [d.get("name") for d in details.get("downstreamProjects", [])]
            })
            
        return jsonify(jobs_detail_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stats")
@login_required if AUTH_ENABLED else lambda x: x
def api_stats():
    try:
        service = get_service()
        jobs = service.get_all_jobs()
        
        success_count = sum(1 for j in jobs if j.get("color", "").startswith("blue"))
        failed_count = sum(1 for j in jobs if j.get("color", "").startswith("red"))
        unstable_count = sum(1 for j in jobs if j.get("color", "").startswith("yellow"))
        
        return jsonify({
            "total_jobs": len(jobs),
            "success_count": success_count,
            "failed_count": failed_count,
            "unstable_count": unstable_count,
            "last_updated": "Just now" # Add JS dynamic later
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)

# trigger reload for config change
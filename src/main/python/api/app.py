import sys
import os
import logging
import yaml
import secrets
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.user import User
from visualization.graph_builder import build_graph
import services.jenkins_service as jenkins_service
import services.mock_service as mock_service

# ═══════════════════════════════════════════════════════
# CONFIGURATION — env vars take priority over config.yaml
# ═══════════════════════════════════════════════════════
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml"))
with open(CONFIG_PATH, encoding="utf-8") as f:
    config = yaml.safe_load(f)

app_config = config.get("app", {})

# App settings from env → config → defaults
DEMO_MODE = os.environ.get("FLOWTRACE_DEMO_MODE", str(app_config.get("demo_mode", False))).lower() in ("true", "1", "yes")
AUTH_ENABLED = os.environ.get("FLOWTRACE_AUTH_ENABLED", str(config.get("auth", {}).get("enabled", True))).lower() in ("true", "1", "yes")
FLASK_ENV = os.environ.get("FLASK_ENV", "production")
IS_PRODUCTION = FLASK_ENV == "production"

# ═══════════════════════════════════════════════════════
# FLASK APP SETUP
# ═══════════════════════════════════════════════════════
app = Flask(__name__, template_folder="templates", static_folder="static")

# Secret key: env var → config → auto-generated (with warning)
secret_key = os.environ.get("FLOWTRACE_SECRET_KEY")
if not secret_key:
    secret_key = config.get("auth", {}).get("secret_key", "")
    if not secret_key or secret_key in ("", "dev-fallback-key", "flowtrace-super-secret-key-change-me"):
        secret_key = secrets.token_hex(32)
        if IS_PRODUCTION:
            print("[WARNING] No FLOWTRACE_SECRET_KEY set. Using auto-generated key.")
            print("          Sessions will be invalidated on restart. Set FLOWTRACE_SECRET_KEY in .env")

app.secret_key = secret_key

# Security headers
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=IS_PRODUCTION,
    WTF_CSRF_ENABLED=True,
    WTF_CSRF_TIME_LIMIT=3600,
)

# ═══════════════════════════════════════════════════════
# CSRF PROTECTION
# ═══════════════════════════════════════════════════════
csrf = CSRFProtect(app)

# Exempt API routes from CSRF (they use auth tokens / session cookies)
# but protect all form POST endpoints
csrf.exempt("graph")
csrf.exempt("api_jobs")
csrf.exempt("api_stats")
csrf.exempt("health_check")

# ═══════════════════════════════════════════════════════
# RATE LIMITING
# ═══════════════════════════════════════════════════════
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per minute"],
    storage_uri="memory://",
)

# ═══════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO if IS_PRODUCTION else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "flowtrace.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("flowtrace")

# ═══════════════════════════════════════════════════════
# FLASK-LOGIN SETUP
# ═══════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════
# AUTH DECORATOR HELPER
# ═══════════════════════════════════════════════════════
def require_auth(f):
    """Conditionally apply @login_required based on AUTH_ENABLED."""
    if AUTH_ENABLED:
        return login_required(f)
    return f

# ═══════════════════════════════════════════════════════
# PAGE ROUTES
# ═══════════════════════════════════════════════════════
@app.route("/")
def index():
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    if not AUTH_ENABLED:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        demo_bypass = request.form.get("demo_bypass")

        if demo_bypass == "true":
            demo_user = User.find_by_username("demo")
            if not demo_user:
                User.create("Demo User", "demo@flowtrace.local", "demo", "demo")
                demo_user = User.find_by_username("demo")
            login_user(demo_user)
            logger.info("Demo user login")
            return redirect(url_for("dashboard"))

        if not username or not password:
            flash("Please enter both username and password", "error")
            return render_template("login.html")

        user = User.find_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            logger.info(f"User '{username}' logged in")
            return redirect(url_for("dashboard"))
        
        logger.warning(f"Failed login attempt for '{username}' from {request.remote_addr}")
        flash("Invalid username or password", "error")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def register():
    if not AUTH_ENABLED:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        # Input validation
        if not all([name, email, username, password, confirm]):
            flash("All fields are required", "error")
            return redirect(url_for("register"))

        if len(username) < 3 or len(username) > 32:
            flash("Username must be 3-32 characters", "error")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters", "error")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match", "error")
            return redirect(url_for("register"))

        if User.create(name, email, username, password):
            logger.info(f"New user registered: '{username}'")
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Username or email already exists", "error")

    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    username = current_user.username if not current_user.is_anonymous else "unknown"
    logout_user()
    logger.info(f"User '{username}' logged out")
    return redirect(url_for("login"))

@app.route("/dashboard")
@require_auth
def dashboard():
    return render_template("dashboard.html", user=current_user if not current_user.is_anonymous else None)

@app.route("/jobs")
@require_auth
def jobs_page():
    return render_template("jobs.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/profile", methods=["GET", "POST"])
@require_auth
def profile_page():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email:
            flash("Name and email are required", "error")
            return render_template("profile.html", user=current_user)

        from werkzeug.security import generate_password_hash
        pwd_hash = generate_password_hash(password) if password else None

        if User.update(current_user.id, name, email, pwd_hash):
            current_user.name = name
            current_user.email = email
            logger.info(f"User '{current_user.username}' updated profile")
            flash("Profile updated successfully", "success")
        else:
            flash("Error updating profile. Email might be in use.", "error")

    return render_template("profile.html", user=current_user)

@app.route("/jenkins-guide")
def guide():
    return render_template("guide.html")

# ═══════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════
@app.route("/api/health")
def health_check():
    """Health check endpoint for monitoring/load balancers."""
    return jsonify({
        "status": "healthy",
        "service": "flowtrace",
        "demo_mode": DEMO_MODE,
        "auth_enabled": AUTH_ENABLED,
    }), 200

@app.route("/api/graph")
@require_auth
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
        logger.error(f"Graph API error: {e}", exc_info=True)
        return jsonify({"error": "Failed to load graph data"}), 500

@app.route("/api/jobs")
@require_auth
def api_jobs():
    try:
        service = get_service()
        jobs = service.get_all_jobs()

        jobs_detail_list = []
        for job in jobs:
            name = job["name"]
            details = service.get_job_details(name)
            last_build = details.get("lastBuild", {}) or {}

            upstream_projects = details.get("upstreamProjects") or []
            downstream_projects = details.get("downstreamProjects") or []

            jobs_detail_list.append({
                "name": name,
                "color": job.get("color", "notbuilt"),
                "build_number": last_build.get("number"),
                "duration": last_build.get("duration"),
                "upstream": [u.get("name") for u in upstream_projects],
                "downstream": [d.get("name") for d in downstream_projects]
            })

        return jsonify(jobs_detail_list)
    except Exception as e:
        logger.error(f"Jobs API error: {e}", exc_info=True)
        return jsonify({"error": "Failed to load jobs data"}), 500

@app.route("/api/stats")
@require_auth
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
            "last_updated": "Just now"
        })
    except Exception as e:
        logger.error(f"Stats API error: {e}", exc_info=True)
        return jsonify({"error": "Failed to load stats"}), 500

# ═══════════════════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════════════════
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"500 error: {e}", exc_info=True)
    return render_template("errors/500.html"), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Rate limit exceeded. Try again later."}), 429

# ═══════════════════════════════════════════════════════
# SECURITY HEADERS
# ═══════════════════════════════════════════════════════
@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if IS_PRODUCTION:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# ═══════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    is_dev = os.environ.get("FLASK_ENV", "development") != "production"
    port = int(os.environ.get("PORT", 5000))

    if is_dev:
        logger.info(f"Starting FlowTrace in DEVELOPMENT mode on port {port}")
        app.run(debug=True, host="127.0.0.1", port=port)
    else:
        logger.info(f"Starting FlowTrace in PRODUCTION mode on port {port}")
        # In production, use: gunicorn -w 4 -b 0.0.0.0:5000 src.main.python.api.app:app
        # Or: waitress-serve --port=5000 src.main.python.api.app:app
        app.run(debug=False, host="0.0.0.0", port=port)
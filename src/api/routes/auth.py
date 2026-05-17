import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from api.utils import AUTH_ENABLED, DEMO_MODE
from api.extensions import limiter

logger = logging.getLogger("flowtrace")
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    if not AUTH_ENABLED:
        return redirect(url_for("pages.dashboard"))

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
            logger.info("Demo user login (demo mode)")
            return redirect(url_for("pages.dashboard"))

        if not username or not password:
            flash("Please enter both username and password", "error")
            return render_template("login.html", demo_mode=DEMO_MODE)

        user = User.find_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            logger.info(f"User '{username}' logged in")
            return redirect(url_for("pages.dashboard"))

        logger.warning(f"Failed login attempt for '{username}' from {request.remote_addr}")
        flash("Invalid username or password", "error")

    return render_template("login.html", demo_mode=DEMO_MODE)

@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def register():
    if not AUTH_ENABLED:
        return redirect(url_for("pages.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not all([name, email, username, password, confirm]):
            flash("All fields are required", "error")
            return redirect(url_for("auth.register"))

        if len(username) < 3 or len(username) > 32:
            flash("Username must be 3-32 characters", "error")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters", "error")
            return redirect(url_for("auth.register"))

        if password != confirm:
            flash("Passwords do not match", "error")
            return redirect(url_for("auth.register"))

        if User.create(name, email, username, password):
            logger.info(f"New user registered: '{username}'")
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("Username or email already exists", "error")

    return render_template("register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    username = current_user.username if not current_user.is_anonymous else "unknown"
    logout_user()
    logger.info(f"User '{username}' logged out")
    return redirect(url_for("auth.login"))

import logging
from flask import Blueprint, render_template, request, flash
from flask_login import current_user
from models.user import User
from api.utils import DEMO_MODE, require_auth

logger = logging.getLogger("flowtrace")
pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/")
def index():
    return render_template("landing.html", demo_mode=DEMO_MODE)

@pages_bp.route("/dashboard")
@require_auth
def dashboard():
    return render_template(
        "dashboard.html",
        user=current_user if not current_user.is_anonymous else None,
    )

@pages_bp.route("/jobs")
@require_auth
def jobs_page():
    return render_template("jobs.html")

@pages_bp.route("/about")
def about():
    return render_template("about.html")

@pages_bp.route("/profile", methods=["GET", "POST"])
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

@pages_bp.route("/jenkins-guide")
def guide():
    return render_template("guide.html")

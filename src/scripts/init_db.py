import sys
import os

# Resolve paths so imports work from any working directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
sys.path.insert(0, PARENT_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(PARENT_DIR, "..", "..", "..", ".env"))

from api.app import app, db
from models.user import User


def init_database():
    """Create tables and seed initial users in Supabase PostgreSQL."""
    with app.app_context():
        # Creates all tables (safe: skips if they already exist)
        db.create_all()
        print("[OK] Tables created successfully.")

        # Check if demo user already exists
        existing = User.query.filter_by(username="demo").first()
        if not existing:
            # Demo user (share with interviewers)
            demo_user = User(
                name="Demo User",
                username="demo",
                email="demo@flowtrace.app",
            )
            demo_user.set_password("Demo@FlowTrace2025")
            db.session.add(demo_user)

            # Admin user (keep private)
            admin_password = os.environ.get("ADMIN_PASSWORD", "Admin@FlowTrace2025")
            admin_user = User(
                name="Admin",
                username="admin",
                email="admin@flowtrace.app",
            )
            admin_user.set_password(admin_password)
            db.session.add(admin_user)

            db.session.commit()
            print("[OK] Demo and admin users created.")
            print("     Demo login:  demo / Demo@FlowTrace2025")
        else:
            print("[OK] Users already exist. Skipping seed.")


if __name__ == "__main__":
    init_database()

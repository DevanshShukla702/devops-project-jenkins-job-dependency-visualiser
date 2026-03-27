from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import OperationalError, IntegrityError
from datetime import datetime
import time

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for FlowTrace authentication (Supabase PostgreSQL)."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ----------------------------------------------------------
    # Static methods preserve the same API that app.py calls,
    # so ALL existing routes work without any changes.
    # ----------------------------------------------------------

    @staticmethod
    def get(user_id):
        """Get user by ID -- used by Flask-Login user_loader."""
        def _query():
            return db.session.get(User, int(user_id))
        return _query_with_retry(_query)

    @staticmethod
    def find_by_username(username):
        """Find user by username."""
        def _query():
            return User.query.filter_by(username=username).first()
        return _query_with_retry(_query)

    @staticmethod
    def create(name, email, username, password):
        """Create a new user. Returns True on success, False if duplicate."""
        try:
            user = User(name=name, email=email, username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False
        except OperationalError:
            db.session.rollback()
            return False

    @staticmethod
    def update(user_id, name, email, new_password_hash=None):
        """Update user profile. Returns True on success."""
        try:
            user = db.session.get(User, int(user_id))
            if user:
                user.name = name
                user.email = email
                if new_password_hash:
                    user.password_hash = new_password_hash
                db.session.commit()
                return True
            return False
        except IntegrityError:
            db.session.rollback()
            return False
        except OperationalError:
            db.session.rollback()
            return False

    def __repr__(self):
        return f"<User {self.username}>"


def _query_with_retry(query_fn, retries=2):
    """Retry database queries to handle Supabase cold starts gracefully."""
    for attempt in range(retries):
        try:
            return query_fn()
        except OperationalError:
            if attempt < retries - 1:
                time.sleep(2)
                db.session.rollback()
            else:
                raise

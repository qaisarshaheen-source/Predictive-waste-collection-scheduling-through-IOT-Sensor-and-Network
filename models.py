from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    location_lat = db.Column(db.Float, default=0.0)
    location_lng = db.Column(db.Float, default=0.0)
    # --- NEW: Add a column to store the formatted location name ---
    location_name = db.Column(db.String(255), nullable=True) 
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class BinAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    compartment = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    sent_email = db.Column(db.Boolean, default=False)

class ScanLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    waste_type = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    confidence = db.Column(db.Float, default=0.0) # Placeholder if we add confidence later
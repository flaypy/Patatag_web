from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Modelo de usuário"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    profile_image = db.Column(db.String(500))  # NOVO CAMPO: URL da foto de perfil
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamento com pets
    pets = db.relationship('Pet', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'profile_image': self.profile_image,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Pet(db.Model):
    """Modelo de pet"""
    __tablename__ = 'pets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50))
    breed = db.Column(db.String(100))
    photo_url = db.Column(db.String(500))
    device_id = db.Column(db.String(100), unique=True)
    api_key = db.Column(db.String(100), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_online = db.Column(db.Boolean, default=False)
    battery_level = db.Column(db.Integer, default=100)
    last_seen = db.Column(db.DateTime)

    locations = db.relationship('Location', backref='pet', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_last_location=False):
        data = {
            'id': self.id,
            'name': self.name,
            'species': self.species,
            'breed': self.breed,
            'photo_url': self.photo_url,
            'device_id': self.device_id,
            'is_online': self.is_online,
            'battery_level': self.battery_level,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_last_location:
            last_location = Location.query.filter_by(pet_id=self.id).order_by(Location.timestamp.desc()).first()
            data['last_location'] = last_location.to_dict() if last_location else None

        return data

# ... (O restante dos modelos Location, GeofenceZone e Alert continua igual) ...
class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    altitude = db.Column(db.Float)
    speed = db.Column(db.Float)
    satellites = db.Column(db.Integer)
    hdop = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'speed': self.speed,
            'satellites': self.satellites,
            'hdop': self.hdop,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class GeofenceZone(db.Model):
    __tablename__ = 'geofence_zones'
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    center_lat = db.Column(db.Float, nullable=False)
    center_lng = db.Column(db.Float, nullable=False)
    radius_meters = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'name': self.name,
            'center_lat': self.center_lat,
            'center_lng': self.center_lng,
            'radius_meters': self.radius_meters,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'alert_type': self.alert_type,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
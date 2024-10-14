from datetime import datetime

from server import db

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    api_token = db.Column(db.String(64), nullable=False, unique=True)
    readings = db.relationship('Readings', backref='event', lazy=True)  # Relacionamento com leituras (associadas a este evento)
    
class Readings(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID único da leitura
    tag_epc = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.String, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)  # Relacionamento com o evento
    collected = db.Column(db.Integer, nullable=False, default=0)
    
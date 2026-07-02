from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Tabla para TI (El administrador)
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Tabla para tus CLIENTES (Prospectos de venta)
class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    servicio = db.Column(db.String(100)) # Ej: "Auditoría Web", "App Flask"
    mensaje = db.Column(db.Text)

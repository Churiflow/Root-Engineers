from app import app, db, Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    # Buscamos si ya existe un admin para no duplicarlo
    admin_existente = Usuario.query.filter_by(username='admin').first()
    
    if admin_existente:
        # Si ya existe, le actualizamos la contraseña por si se nos olvidó
        admin_existente.password = generate_password_hash('admin123', method='pbkdf2:sha256')
        print(">>> Usuario 'admin' ya existía. Contraseña actualizada a: admin123")
    else:
        # Si no existe, lo creamos de cero
        nuevo_admin = Usuario(
            username='admin', 
            password=generate_password_hash('admin123', method='pbkdf2:sha256')
        )
        db.session.add(nuevo_admin)
        print(">>> Nuevo usuario 'admin' creado con éxito. Contraseña: admin123")
    
    db.session.commit()
    print(">>> Cambios guardados en la base de datos.")

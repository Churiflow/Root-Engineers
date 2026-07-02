import requests # Agrega esto al inicio de app.py
import re # Agrega esto al inicio de app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Usuario, Lead # Importamos tus tablas
from fpdf import FPDF
from flask import send_file, make_response
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_llave_super_secreta_red_team' # Cambia esto
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///empresa.db'

db.init_app(app)

@app.route('/escanear', methods=['POST'])
@login_required
def escanear():
    url = request.form.get('url')
    if not url.startswith('http'):
        url = 'https://' + url
    
    try:
        # Hacemos una petición rápida a la web objetivo
        response = requests.get(url, timeout=5)
        headers = response.headers
        
        # Analizamos qué servidor usa y si tiene seguridad
        resultado = {
            "servidor": headers.get('Server', 'No detectado'),
            "seguridad_hsts": "SÍ" if 'Strict-Transport-Security' in headers else "NO",
            "proteccion_clickjacking": "SÍ" if 'X-Frame-Options' in headers else "NO",
            "tecnologia": headers.get('X-Powered-By', 'Oculta')
        }
        return render_template('admin.html', leads=Lead.query.all(), scan=resultado, target=url)
    
    except Exception as e:
        flash(f"Error al analizar: {str(e)}")
        return redirect(url_for('admin'))

@app.route('/')
def index():
    # Esta función busca el archivo templates/index.html y lo muestra
    return render_template('index.html')

# --- CONFIGURACIÓN DE SESIONES ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Si alguien no está logueado, lo manda aquí

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# --- RUTAS DE ACCESO ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        
        usuario_db = Usuario.query.filter_by(username=user).first()
        
        # Verificamos si existe y si la contraseña coincide con el Hash
        if usuario_db and check_password_hash(usuario_db.password, pw):
            login_user(usuario_db)
            return redirect(url_for('admin')) # ¡Aquí es donde te dirige al Admin!
        else:
            flash('Acceso denegado: Credenciales no válidas.')
            
    return render_template('login.html')

@app.route('/admin')
@login_required # Solo tú puedes ver esto
def admin():
    proyectos = Lead.query.all()
    return render_template('admin.html', leads=proyectos)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- RUTA PARA GUARDAR CLIENTES ---
@app.route('/contacto', methods=['POST'])
def contacto():
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    servicio = request.form.get('servicio')
    mensaje = request.form.get('mensaje')
    
    nuevo_cliente = Lead(nombre=nombre, email=email, servicio=servicio, mensaje=mensaje)
    db.session.add(nuevo_cliente)
    db.session.commit()
    
    return redirect(url_for('index'))


@app.route('/auditar_lead/<int:id>')
@login_required
def auditar_lead(id):
    cliente = Lead.query.get_or_404(id)
    texto_completo = cliente.mensaje
    
    # EXPRESIÓN REGULAR: Busca algo que parezca una URL dentro del texto
    url_encontrada = re.search(r'(https?://[^\s]+|[a-z0-9.-]+\.[a-z]{2,})', texto_completo, re.IGNORECASE)
    
    if url_encontrada:
        target_url = url_encontrada.group(0)
        
        # Limpieza estándar
        if not target_url.startswith('http'):
            target_url = 'https://' + target_url
            
        try:
            # Ejecutamos el escaneo real
            response = requests.get(target_url, timeout=5)
            headers = response.headers
            resultado = {
                "servidor": headers.get('Server', 'Oculta'),
                "seguridad_hsts": "SÍ" if 'Strict-Transport-Security' in headers else "NO",
                "proteccion_clickjacking": "SÍ" if 'X-Frame-Options' in headers else "NO"
            }
            return render_template('admin.html', leads=Lead.query.all(), scan=resultado, target=target_url)
        except:
            flash(f"No se pudo conectar con {target_url}")
    else:
        flash("No encontré ninguna URL válida en el mensaje del cliente.")
        
    return redirect(url_for('admin'))


from fpdf import FPDF
from flask import send_file, make_response
import io

@app.route('/generar_pdf/<int:id>')
@login_required
def generar_pdf(id):
    cliente = Lead.query.get_or_404(id)
    
    # Configuración del PDF
    pdf = FPDF()
    pdf.add_page()
    
    # --- CABECERA ESTILO HACKER ---
    pdf.set_fill_color(10, 15, 20) # Fondo casi negro
    pdf.rect(0, 0, 210, 50, 'F')
    
    pdf.set_font("helvetica", 'B', 24)
    pdf.set_text_color(0, 255, 127) # Verde Neón
    pdf.cell(0, 25, "TECHSECURE AUDIT SYSTEM", ln=True, align='C')
    
    pdf.set_font("helvetica", 'B', 10)
    pdf.set_text_color(255, 255, 255) # Blanco
    pdf.cell(0, -5, "INFORME PRELIMINAR DE VULNERABILIDADES", ln=True, align='C')
    
    # --- DATOS DEL CLIENTE ---
    pdf.ln(35)
    pdf.set_text_color(0, 0, 0) # Volver a negro para el texto
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, f"CLIENTE: {cliente.nombre.upper()}", ln=True)
    pdf.set_font("helvetica", '', 11)
    pdf.cell(0, 10, f"EMAIL DE CONTACTO: {cliente.email}", ln=True)
    pdf.cell(0, 10, f"OBJETIVO DETECTADO: {cliente.mensaje}", ln=True)
    
    # --- CUERPO DEL REPORTE ---
    pdf.ln(10)
    pdf.set_font("helvetica", 'B', 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, " ANALISIS TECNICO INICIAL", ln=True, fill=True)
    
    pdf.ln(5)
    pdf.set_font("helvetica", '', 11)
    texto_analisis = (
        "Tras recibir su solicitud, nuestro sistema TechSecure ha realizado un escaneo superficial "
        "de las cabeceras de seguridad de su servidor. Se recomienda una auditoria profunda "
        "para mitigar riesgos de inyeccion de codigo, Clickjacking y ataques Man-in-the-Middle.\n\n"
        "ESTADO: PENDIENTE DE REVISION MANUAL."
    )
    pdf.multi_cell(0, 8, texto_analisis)
    
    # --- FIRMA ---
    pdf.ln(30)
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 10, "Analista Responsable:", ln=True)
    pdf.set_font("helvetica", 'I', 11)
    pdf.cell(0, 10, "TechSecure Lead Engineer - Red Team Division", ln=True)

    # --- GENERAR ARCHIVO ---
    # fpdf2 devuelve bytes con .output()
    pdf_bytes = pdf.output()
    
    return send_file(
        io.BytesIO(pdf_bytes),
        download_name=f"Reporte_{cliente.nombre}.pdf",
        as_attachment=True,
        mimetype='application/pdf'
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Crea las tablas si no existen
    app.run(debug=True, host='0.0.0.0', port=5000)

@app.route('/api/check_leads')
@login_required
def check_leads():
    count = Lead.query.count()
    return {"count": count}

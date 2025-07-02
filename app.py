"""
GCDM Auto Flask Application
Main application entry point
"""

from flask import Flask
import os

# Initialize Flask app
app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# Configuration
app.config['SECRET_KEY'] = 'gcdmauto-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gcdmauto.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database
from app.models import db
db.init_app(app)

# Import models after db initialization
from app.models import ExcelData, DataPeriod

# Initialize security
from app.security import init_security
init_security(app)

# Import controllers
from app.controllers import excel_bp, admin_bp, config_bp

# Register blueprints
app.register_blueprint(excel_bp, url_prefix='/excel')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(config_bp, url_prefix='/config')

@app.route('/')
def index():
    """Home page redirects to Excel upload"""
    from flask import redirect, url_for
    return redirect(url_for('excel.upload'))

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Security check: Ensure we're only running on localhost
    import socket
    hostname = socket.gethostname()
    print(f"Starting GCDM Auto Flask Application on {hostname}")
    print("Security: Application will only accept connections from localhost (127.0.0.1)")
    print("Access URL: http://127.0.0.1:8080")

    # Run the application (localhost only for security)
    app.run(host='127.0.0.1', port=8080, debug=True, threaded=True)

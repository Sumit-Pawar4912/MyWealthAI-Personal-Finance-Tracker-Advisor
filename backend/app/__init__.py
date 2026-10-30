from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# DATABASE_URL accepts PostgreSQL URLs such as
# postgresql+psycopg://user:password@localhost:5432/mywelthai.
database_url = os.getenv('DATABASE_URL', 'sqlite:///mywelthai.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql+psycopg://', 1)
elif database_url.startswith('postgresql://'):
    database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
    'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '20')),
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
if database_url.startswith('sqlite:'):
    app.config['SQLALCHEMY_ENGINE_OPTIONS']['connect_args'] = {
        'timeout': 20,
        'check_same_thread': False,
    }

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize database
from app.database import db
db.init_app(app)

# Register blueprints (routes)
from app.routes import auth_routes, transaction_routes, dashboard_routes, advice_routes, analytics_routes, chatbot_routes, admin_routes, report_routes

app.register_blueprint(auth_routes.bp)
app.register_blueprint(transaction_routes.bp)
app.register_blueprint(dashboard_routes.bp)
app.register_blueprint(advice_routes.bp)
app.register_blueprint(analytics_routes.bp)
app.register_blueprint(chatbot_routes.chatbot_bp)
app.register_blueprint(admin_routes.bp)
app.register_blueprint(report_routes.bp)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return {
        'message': 'Welcome to MyWelthAI Backend API',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'auth': '/api/auth',
            'transactions': '/api/transactions',
            'dashboard': '/api/dashboard',
            'advice': '/api/advice'
        },
        'frontend': 'http://localhost:5174'
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'app': 'MyWelthAI Backend'
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

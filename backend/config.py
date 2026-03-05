import os
from dotenv import load_dotenv

load_dotenv()

# Flask Configuration
class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///mywelthai.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyD6hX76Smhvm_8TAweqIpApYnbkKqJ8rKY')
    GEMINI_MODEL = 'gemini-2.0-flash'
    
    # SQLite connection settings to prevent "database is locked" error
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'timeout': 15,  # Wait up to 15 seconds for lock release
            'check_same_thread': False,  # Allow multiple threads to access DB
        },
        'pool_size': 10,
        'pool_recycle': 3600,  # Recycle connections after 1 hour
        'pool_pre_ping': True,  # Test connection before using
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Get config from environment
config_name = os.getenv('FLASK_ENV', 'development')
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
config = config.get(config_name, DevelopmentConfig)

import os
import sys
from app import app
from app.database import db

# Set UTF-8 encoding for console output
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Create tables before running the app
with app.app_context():
    db.create_all()
    print("[OK] Database tables created successfully!")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    # Disable debug mode for proper connection pooling (use FLASK_ENV=development for auto-reload)
    debug = False
    print(f"[START] MyWelthAI Backend on http://localhost:{port}")
    app.run(debug=debug, host='0.0.0.0', port=port, threaded=True)

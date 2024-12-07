from flask import Flask
from models import ensure_table_exists
from routes import register_routes

app = Flask(__name__)

# Ensure the database table exists before running the application
ensure_table_exists()

# Register all routes
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask
from models import ensure_table_exists
from routes import register_routes
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# Ensure the database table exists
ensure_table_exists()

# Register routes
register_routes(app)

# Swagger UI setup
SWAGGER_URL = '/swagger'  # URL under which Swagger UI will be accessible
API_URL = '/static/swagger.json'  # Path to your swagger.json file

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={  # Swagger UI configuration
        'app_name': "Game Data API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    app.run(debug=True)

import datetime
import jwt
from functools import wraps
from flask import request, jsonify
from services import GameDataService
import requests
import csv
from io import StringIO
from utils import parse_csv_data
from models import get_connection

def register_routes(app):

    # Set the secret key for JWT. In production, keep this secret and safe.
    app.config['SECRET_KEY'] = 'your_secret_key_here'

    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None

            # JWT is expected to be in the Authorization header in the format: Bearer <token>
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                parts = auth_header.split()
                if len(parts) == 2 and parts[0].lower() == 'bearer':
                    token = parts[1]

            if not token:
                return jsonify({"message": "Token is missing!"}), 401

            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                # Optionally, you can store and check user info from data if needed.
            except jwt.ExpiredSignatureError:
                return jsonify({"message": "Token has expired!"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"message": "Invalid token!"}), 401

            return f(*args, **kwargs)
        return decorated

    @app.route('/login', methods=['POST'])
    def login():
        # Expecting JSON with username and password
        auth_data = request.get_json()
        if not auth_data or 'username' not in auth_data or 'password' not in auth_data:
            return jsonify({"message": "Username and password required"}), 400

        username = auth_data['username']
        password = auth_data['password']

        # Hardcoded credentials check
        if username == "username" and password == "password":
            # Create a token with an expiration
            token = jwt.encode({
                'user': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            return jsonify({"message": "Login successful", "token": token}), 200
        else:
            return jsonify({"message": "Invalid credentials"}), 401

    @app.route('/data', methods=['POST'])
    @token_required
    def get_game_data():
        try:
            req = request.json
            results, row_count = GameDataService.get_data(req)
            return jsonify({
                "message": "Data fetched successfully",
                "data": {"rows": results, "rowCount": row_count}
            })
        except Exception as e:
            return jsonify({
                "message": f"Error occurred: {str(e)}",
                "data": None
            }), 500

    @app.route('/upload-csv', methods=['POST'])
    @token_required
    def upload_csv():
        try:
            # Get the CSV link from the request
            data = request.json
            csv_link = data.get('csv_link')
            if not csv_link:
                return jsonify({
                    "message": "CSV link (csv_link) is required.",
                    "data": None
                }), 400

            # Download the CSV file
            response = requests.get(csv_link)
            if response.status_code != 200:
                return jsonify({
                    "message": "Failed to download the CSV file / Invalid URL.",
                    "data": None
                }), 400

            # Read and process CSV data
            csv_content = StringIO(response.text)
            csv_reader = csv.DictReader(csv_content)
            csv_data = parse_csv_data(csv_reader)

            # Prepare data for bulk insert
            values = [
                (
                    row['appid'], row['name'], row['release_date'], row['required_age'], row['price'],
                    row['dlc_count'], row['about_the_game'], row['supported_languages'], row['windows'],
                    row['mac'], row['linux'], row['positive'], row['negative'], row['score_rank'],
                    row['developers'], row['publishers'], row['categories'], row['genres'], row['tags']
                )
                for row in csv_data
            ]

            # Insert data into the game_data table using ON CONFLICT to overwrite duplicates
            connection = get_connection()
            with connection.cursor() as cursor:
                insert_query = """
                    INSERT INTO public.game_data (
                        appid, "name", release_date, required_age, price, dlc_count, 
                        about_the_game, supported_languages, windows, mac, linux, 
                        positive, negative, score_rank, developers, publishers, 
                        categories, genres, tags
                    ) 
                    VALUES %s
                    ON CONFLICT (appid) DO UPDATE 
                    SET 
                        "name" = EXCLUDED."name", 
                        release_date = EXCLUDED.release_date,
                        required_age = EXCLUDED.required_age,
                        price = EXCLUDED.price,
                        dlc_count = EXCLUDED.dlc_count,
                        about_the_game = EXCLUDED.about_the_game,
                        supported_languages = EXCLUDED.supported_languages,
                        windows = EXCLUDED.windows,
                        mac = EXCLUDED.mac,
                        linux = EXCLUDED.linux,
                        positive = EXCLUDED.positive,
                        negative = EXCLUDED.negative,
                        score_rank = EXCLUDED.score_rank,
                        developers = EXCLUDED.developers,
                        publishers = EXCLUDED.publishers,
                        categories = EXCLUDED.categories,
                        genres = EXCLUDED.genres,
                        tags = EXCLUDED.tags;
                """
                from psycopg2.extras import execute_values
                execute_values(cursor, insert_query, values)
                connection.commit()

            return jsonify({
                "message": "CSV data successfully uploaded.",
                "data": None
            }), 200

        except Exception as e:
            return jsonify({
                "message": f"Error occurred: {str(e)}",
                "data": None
            }), 500
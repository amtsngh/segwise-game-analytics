from flask import request, jsonify
from services import GameDataService
import requests
import csv
from io import StringIO
from utils import parse_csv_data
from models import get_connection

def register_routes(app):

    @app.route('/data', methods=['POST'])
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
                # Use psycopg2's execute_values for bulk insert
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
from flask import request, jsonify
from services import GameDataService
import requests
import csv
from io import StringIO
from utils import parse_date, parse_csv_data

def register_routes(app):

    @app.route('/data', methods=['POST'])
    def get_game_data():
        req = request.json
        results, row_count = GameDataService.get_data(req)
        return jsonify({"data": results, "rowCount": row_count})

    @app.route('/upload-csv', methods=['POST'])
    def upload_csv():
        try:
            # Get the CSV link from the request
            data = request.json
            csv_link = data.get('csv_link')
            if not csv_link:
                return jsonify({"error": "CSV link is required."}), 400

            # Download the CSV file
            response = requests.get(csv_link)
            if response.status_code != 200:
                return jsonify({"error": "Failed to download the CSV file."}), 400

            # Read and process CSV data
            csv_content = StringIO(response.text)
            csv_reader = csv.DictReader(csv_content)
            csv_data = parse_csv_data(csv_reader)

            # Insert data into the game_data table
            connection = get_connection()
            with connection.cursor() as cursor:
                for row in csv_data:
                    insert_query = """
                        INSERT INTO public.game_data (
                            appid, "name", release_date, required_age, price, dlc_count, 
                            about_the_game, supported_languages, windows, mac, linux, 
                            positive, negative, score_rank, developers, publishers, 
                            categories, genres, tags
                        ) 
                        VALUES (
                            %(appid)s, %(name)s, %(release_date)s, %(required_age)s, %(price)s, 
                            %(dlc_count)s, %(about_the_game)s, %(supported_languages)s, 
                            %(windows)s, %(mac)s, %(linux)s, %(positive)s, %(negative)s, 
                            %(score_rank)s, %(developers)s, %(publishers)s, %(categories)s, 
                            %(genres)s, %(tags)s
                        );
                    """
                    cursor.execute(insert_query, row)
                connection.commit()

            return jsonify({"message": "CSV data successfully uploaded."}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
import psycopg2
from config import Config

# Database connection
def get_connection():
    return psycopg2.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )

def ensure_table_exists():
    """Ensures the game_data table exists in the database."""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'game_data');")
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                table_columns = """
                    slno SERIAL PRIMARY KEY,
                    AppID INT UNIQUE,
                    Name VARCHAR(255),
                    Release_date DATE,
                    Required_age INT,
                    Price FLOAT,
                    DLC_count INT,
                    About_the_game TEXT,
                    Supported_languages JSON,
                    Windows BOOLEAN,
                    Mac BOOLEAN,
                    Linux BOOLEAN,
                    Positive INT,
                    Negative INT,
                    Score_rank INT,
                    Developers TEXT,
                    Publishers TEXT,
                    Categories JSON,
                    Genres JSON,
                    Tags JSON
                """
                create_table_sql = f"CREATE TABLE game_data ({table_columns})"
                cursor.execute(create_table_sql)
                connection.commit()
                print("Table 'game_data' created successfully.")
            else:
                print("Table 'game_data' already exists.")
    except Exception as e:
        print(f"Error ensuring table exists: {e}")

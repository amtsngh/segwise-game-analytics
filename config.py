import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_NAME = os.getenv("DB_NAME", "postgres")
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
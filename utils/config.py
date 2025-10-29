import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    API_KEY = os.getenv('FIXER_API_KEY')
    
    # Database Configuration
    DB_NAME = os.getenv('DB_NAME', 'fx_rates_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    
    # Update frequency in minutes
    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '60'))
    
    # Dashboard Configuration
    DASH_PORT = int(os.getenv('DASH_PORT', '8050'))
    DASH_DEBUG = os.getenv('DASH_DEBUG', 'False') == 'True'
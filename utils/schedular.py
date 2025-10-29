import schedule # type: ignore
import time
from datetime import datetime, timedelta
from src.fixer_client import FixerClient
from src.database import save_fx_rate
# from .clean_data import clean_fx_data, validate_fx_data
from utils.config import Config

def update_fx_rates():
    """Fetch and store latest FX rates"""
    client = FixerClient(Config.API_KEY)
    
    try:
        # Get today's date and 30 days ago
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Fetch historical data
        target_currencies = ['USD', 'GBP', 'JPY', 'EUR']
        historical_data = client.get_historical_data(
            start_date=start_date,
            end_date=end_date,
            target_currencies=target_currencies
        )
        
        if historical_data:
            # Save to database
            save_fx_rate(historical_data)
            print(f"Historical FX rates updated successfully")
        else:
            print("No historical data received")
            
    except Exception as e:
        print(f"Error updating FX rates: {e}")

def start_scheduler():
    """Start the scheduler for automated updates"""
    # Schedule updates based on configured interval
    schedule.every(Config.UPDATE_INTERVAL).minutes.do(update_fx_rates)
    
    # Run initial update
    update_fx_rates()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)
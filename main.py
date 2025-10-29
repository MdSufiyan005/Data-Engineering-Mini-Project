import sys
from src import database
from utils import schedular
from src import dashboard
import threading

def main():
    try:
        # Initialize database
        database.init_database()
        
        # Start the scheduler in a separate thread
        scheduler_thread = threading.Thread(target=schedular.start_scheduler)  # Remove the ()
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        # Run the dashboard (this will block)
        dashboard.run_dashboard()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
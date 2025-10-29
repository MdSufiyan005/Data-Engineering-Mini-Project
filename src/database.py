import psycopg2 # type: ignore
from psycopg2 import sql # type: ignore
from  utils.config import Config


def connect_db():
    """Establish a connection to the PostgreSQL database."""
    try:
        connection = psycopg2.connect(
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            host=Config.DB_HOST,
            port=Config.DB_PORT
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
    
def init_database():
    """Initialize the database with required tables"""
    
    create_tables_query = """
    CREATE TABLE IF NOT EXISTS fx_rates (
        id SERIAL PRIMARY KEY,
        currency VARCHAR(3) NOT NULL,
        rate DECIMAL(16,6) NOT NULL,
        base_currency VARCHAR(3) NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_currency_timestamp 
    ON fx_rates(currency, timestamp);
    """
    
    try:
        conn = connect_db()
        with conn.cursor() as cur:
            cur.execute(create_tables_query)
        conn.commit()
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()



def query_fx_rates(currency):
    """Query the FX rates for a specific currency from the database."""
    connection = connect_db()
    if connection is None:
        return None

    cursor = connection.cursor()
    query = sql.SQL("""
        SELECT rate, timestamp 
        FROM fx_rates 
        WHERE currency = %s
        ORDER BY timestamp ASC
    """)

    try:
        cursor.execute(query, (currency,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Database query error: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def save_fx_rate(rate_data):
    """Save the fetched FX rates to the PostgreSQL database."""
    connection = connect_db()
    if connection is None:
        return

    cursor = connection.cursor()
    insert_query = sql.SQL("""
        INSERT INTO fx_rates (currency, rate, base_currency, timestamp)
        VALUES (%s, %s, %s, %s)
    """)

    try:
        for rate in rate_data:
            cursor.execute(insert_query, (
                rate['currency'], 
                rate['rate'], 
                'EUR',  # Base currency is always EUR for Fixer.io
                rate['timestamp']
            ))
        connection.commit()
    except Exception as e:
        print(f"Error saving FX rates: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
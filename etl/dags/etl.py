from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.session import provide_session
from airflow.models import Connection
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import json

# Create connections
@provide_session
def create_connections(session=None):
    # Create PostgreSQL connection
    postgres_conn = Connection(
        conn_id='my_postgres_connection',
        conn_type='postgres',
        host='postgres',  
        schema='postgres',
        login='postgres',
        password='postgres',
        port=5432
    )
    
    # Create CoinGecko API connection
    coingecko_conn = Connection(
        conn_id='coingecko_api',
        conn_type='http',
        host='api.coingecko.com'
    )
    
    # Check if connections already exist and create if they don't
    if not session.query(Connection).filter(Connection.conn_id == postgres_conn.conn_id).first():
        session.add(postgres_conn)
        print(f"Created connection: {postgres_conn.conn_id}")
    
    if not session.query(Connection).filter(Connection.conn_id == coingecko_conn.conn_id).first():
        session.add(coingecko_conn)
        print(f"Created connection: {coingecko_conn.conn_id}")
    
    session.commit()

# Add this to your existing DAG file
@task
def setup_connections():
    create_connections()
    return "Connections created successfully"

# Step 1: Create the tables
@task 
def create_tables():
    postgres_hook = PostgresHook(postgres_conn_id = 'my_postgres_connection')
    # DROP TABLE IF EXISTS cryptocurrencies CASCADE;
    # DROP TABLE IF EXISTS market_data CASCADE;
    # Create main cryptocurrency table
    create_crypto_table = """
        CREATE TABLE IF NOT EXISTS cryptocurrencies (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100),
            hashing_algorithm VARCHAR(50),
            genesis_date DATE,
            market_cap_rank INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            current_price_usd NUMERIC,
            market_cap_usd NUMERIC,
            total_volume_usd NUMERIC,
            ath_usd NUMERIC,
            ath_date_usd TIMESTAMP,
            atl_usd NUMERIC,
            atl_date_usd TIMESTAMP,
            price_change_percentage_24h NUMERIC,
            price_change_percentage_7d NUMERIC,
            price_change_percentage_14d NUMERIC,
            price_change_percentage_30d NUMERIC,
            price_change_percentage_60d NUMERIC,
            price_change_percentage_200d NUMERIC,
            price_change_percentage_1y NUMERIC,
            market_cap_change_24h_usd NUMERIC,
            market_cap_change_percentage_24h NUMERIC,
            high_24h_usd NUMERIC,
            low_24h_usd NUMERIC,
            circulating_supply NUMERIC,
            max_supply NUMERIC,
            total_supply NUMERIC,
            fully_diluted_valuation_usd NUMERIC
        );
    """

    create_market_table = """
        CREATE TABLE IF NOT EXISTS market_data (
            id VARCHAR(50) REFERENCES cryptocurrencies(id),
            date TIMESTAMP,
            prices NUMERIC,
            market_cap NUMERIC,
            total_volumes NUMERIC
        );
            """
    
    postgres_hook.run(create_crypto_table)
    postgres_hook.run(create_market_table)


def extract_crypto(coin):
    return SimpleHttpOperator(
        task_id=f'extract_crypto_{coin}',
        http_conn_id='coingecko_api',
        endpoint=f'/api/v3/coins/{coin}',
        method='GET',
        headers={"accept": "application/json"},
        response_filter=lambda response: json.loads(response.text),
        retry_delay=timedelta(minutes=1),  # Wait 1 minute between retries
        retries=5,  # Maximum number of retries
        retry_exponential_backoff=True,  # Exponential backoff between retries
        dag=dag
    )

def extract_history(coin, current_timestamp, past_timestamp):
    return SimpleHttpOperator(
        task_id=f'extract_history_{coin}',
        http_conn_id='coingecko_api',
        endpoint=f'/api/v3/coins/{coin}/market_chart/range?vs_currency=usd&from={past_timestamp}&to={current_timestamp}',
        method='GET',
        headers={"accept": "application/json"},
        response_filter=lambda response: json.loads(response.text),
        retry_delay=timedelta(minutes=1),
        retries=5,
        retry_exponential_backoff=True,
        dag=dag
    )

# Step 3: Transform the data
@task
def transform_crypto_data(response, coin_id):
    crypto_data = {
        'id': response.get('id', ''),
        'name': response.get('name', ''),
        'hashing_algorithm': response.get('hashing_algorithm', ''),
        'genesis_date': response.get('genesis_date', ''),
        'market_cap_rank': response.get('market_cap_rank', None),
        'current_price_usd': response.get('market_data', {}).get('current_price', {}).get('usd'),
        'market_cap_usd': response.get('market_data', {}).get('market_cap', {}).get('usd'),
        'total_volume_usd': response.get('market_data', {}).get('total_volume', {}).get('usd'),
        'ath_usd': response.get('market_data', {}).get('ath', {}).get('usd'),
        'ath_date_usd': response.get('market_data', {}).get('ath_date', {}).get('usd'),
        'atl_usd': response.get('market_data', {}).get('atl', {}).get('usd'),
        'atl_date_usd': response.get('market_data', {}).get('atl_date', {}).get('usd'),
        'price_change_percentage_24h': response.get('market_data', {}).get('price_change_percentage_24h'),
        'price_change_percentage_7d': response.get('market_data', {}).get('price_change_percentage_7d'),
        'price_change_percentage_14d': response.get('market_data', {}).get('price_change_percentage_14d'),
        'price_change_percentage_30d': response.get('market_data', {}).get('price_change_percentage_30d'),
        'price_change_percentage_60d': response.get('market_data', {}).get('price_change_percentage_60d'),
        'price_change_percentage_200d': response.get('market_data', {}).get('price_change_percentage_200d'),
        'price_change_percentage_1y': response.get('market_data', {}).get('price_change_percentage_1y'),
        'market_cap_change_24h_usd': response.get('market_data', {}).get('market_cap_change_24h'),
        'market_cap_change_percentage_24h': response.get('market_data', {}).get('market_cap_change_percentage_24h'),
        'high_24h_usd': response.get('market_data', {}).get('high_24h', {}).get('usd'),
        'low_24h_usd': response.get('market_data', {}).get('low_24h', {}).get('usd'),
        'circulating_supply': response.get('market_data', {}).get('circulating_supply'),
        'max_supply': response.get('market_data', {}).get('max_supply'),
        'total_supply': response.get('market_data', {}).get('total_supply'),
        'fully_diluted_valuation_usd': response.get('market_data', {}).get('fully_diluted_valuation', {}).get('usd')
    }


    return crypto_data

@task
def transform_market_history(response, coin_id):

    market_data = []
    
    # Get prices, market caps, and volumes data
    prices = response.get('prices', [])
    market_caps = response.get('market_caps', [])
    volumes = response.get('total_volumes', [])
    
    # Transform into rows
    for i in range(len(prices)):
        market_data.append({
            'id': coin_id,
            'date': prices[i][0],  # timestamp
            'prices': prices[i][1],
            'market_cap': market_caps[i][1],
            'total_volumes': volumes[i][1]
        })
    
    return market_data

# Step 4: Load data to PostgreSQL
@task
def load_data_to_postgres(crypto_data, market_data):
    postgres_hook = PostgresHook(postgres_conn_id='my_postgres_connection')
    
    # Insert cryptocurrency data
# Insert cryptocurrency data with explicit column names
    insert_crypto_query = """
    INSERT INTO cryptocurrencies (
        id, name, hashing_algorithm, 
        genesis_date, market_cap_rank, current_price_usd, 
        market_cap_usd, total_volume_usd, ath_usd, ath_date_usd,
        atl_usd, atl_date_usd, price_change_percentage_24h,
        price_change_percentage_7d, price_change_percentage_14d,
        price_change_percentage_30d, price_change_percentage_60d,
        price_change_percentage_200d, price_change_percentage_1y,
        market_cap_change_24h_usd, market_cap_change_percentage_24h,
        high_24h_usd, low_24h_usd, circulating_supply,
        max_supply, total_supply, fully_diluted_valuation_usd
    ) VALUES (
        %(id)s, %(name)s, %(hashing_algorithm)s,
        %(genesis_date)s, %(market_cap_rank)s, %(current_price_usd)s,
        %(market_cap_usd)s, %(total_volume_usd)s, %(ath_usd)s, %(ath_date_usd)s,
        %(atl_usd)s, %(atl_date_usd)s, %(price_change_percentage_24h)s,
        %(price_change_percentage_7d)s, %(price_change_percentage_14d)s,
        %(price_change_percentage_30d)s, %(price_change_percentage_60d)s,
        %(price_change_percentage_200d)s, %(price_change_percentage_1y)s,
        %(market_cap_change_24h_usd)s, %(market_cap_change_percentage_24h)s,
        %(high_24h_usd)s, %(low_24h_usd)s, %(circulating_supply)s,
        %(max_supply)s, %(total_supply)s, %(fully_diluted_valuation_usd)s
    )
    ON CONFLICT (id) DO UPDATE SET
        current_price_usd = EXCLUDED.current_price_usd,
        market_cap_usd = EXCLUDED.market_cap_usd,
        total_volume_usd = EXCLUDED.total_volume_usd,
        market_cap_rank = EXCLUDED.market_cap_rank,
        price_change_percentage_24h = EXCLUDED.price_change_percentage_24h
    """

    # Execute using dictionary parameters instead of list
    with postgres_hook.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(insert_crypto_query, crypto_data)
            
            # Insert market history data
            for row in market_data:
                cur.execute("""
                    INSERT INTO market_data (id, date, prices, market_cap, total_volumes)
                    VALUES (%(id)s, TO_TIMESTAMP(%(date)s / 1000), %(prices)s, %(market_cap)s, %(total_volumes)s);
                """, row)
        conn.commit()
    
# Define the Dag
with DAG(
    dag_id = 'crypto_data',
    start_date = days_ago(1),
    schedule_interval = '@monthly',  # Runs every month
    catchup = False
) as dag:
    # Setup connections first
    connections_setup = setup_connections()
    
    coins = ['bitcoin', 'ethereum', 'litecoin', 'solana', 'dogecoin'] # Feel free to add more coins to the list.

    # Get current timestamp
    current_date = datetime.now()
    current_timestamp = int(current_date.timestamp())

    # Get timestamp for 365 days ago
    past_date = current_date - timedelta(days=365)
    past_timestamp = int(past_date.timestamp())
    
    # Create tables first
    create_tables = create_tables()
    
    # Dictionary to store tasks for each coin
    coin_tasks = {}
    
    # Process each coin
    for coin in coins:
        
        # Create tasks with unique IDs
        extract_current = extract_crypto(coin)
        extract_hist = extract_history(coin, current_timestamp, past_timestamp)
        transform_crypto = transform_crypto_data.override(task_id=f'transform_crypto_{coin}')(extract_current.output, coin)
        transform_market = transform_market_history.override(task_id=f'transform_market_{coin}')(extract_hist.output, coin)
        load_data = load_data_to_postgres.override(task_id=f'load_data_{coin}')(transform_crypto, transform_market)
        
        # Store tasks in dictionary
        coin_tasks[coin] = {
            'extract_current': extract_current,
            'extract_hist': extract_hist,
            'transform_crypto': transform_crypto,
            'transform_market': transform_market,
            'load_data': load_data
        }
        
        # Set dependencies for this coin
        connections_setup >> create_tables >> extract_current >> extract_hist >> transform_crypto >> transform_market >> load_data

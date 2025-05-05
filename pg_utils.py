import psycopg2
import config_utils

# Connect to the PostgreSQL database using the parameters from database.ini file.
def connect():
    conn = None
    try:
        params = config_utils.get_config('config.ini', 'postgresql')
        conn = psycopg2.connect(**params)
        # print("Connected to the PostgreSQL database using parameters", params)
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
    return conn

def fetch_data(query):
    try:
        conn = connect()
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()
            
def fetch_images_with_query(query):
    if query is None:
        print("Query is None. Returning empty list.")
        return []
    
    if query == 'with_face':
        query_string = "SELECT image_uuid, image_url FROM metastore WHERE has_face IS NOT NULL AND image_url IS NOT NULL LIMIT 28;"
    elif query == 'with_glasses':
        query_string = "SELECT image_uuid, image_url FROM metastore WHERE has_glasses IS NOT NULL AND image_url IS NOT NULL LIMIT 28;"
    else:
        query_string = "SELECT image_uuid, image_url FROM metastore WHERE image_url IS NOT NULL LIMIT 28;"

    try:
        conn = connect()
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            rows = cursor.fetchall()
            return rows
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()
    

def fetch_data_in_batches(conn, query, batch_size=1000):
    try:
        conn.autocommit = False
        with conn.cursor('server_side_cursor') as cursor:
            cursor.execute(query)
            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break
                yield rows
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()
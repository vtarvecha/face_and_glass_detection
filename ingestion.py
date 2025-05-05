from datasets import load_dataset 
import os
import psycopg2
from configparser import ConfigParser
import uuid
import sys
import pg_utils
import config_utils

def main():
    # Check if the file name argument is provided, otherwise return. 
    if len(sys.argv) < 2:
        print("Usage: python ingestion.py <file_name>")
        exit(1)
    
    # Load the dataset from the data folder using datasets library   
    file_name = sys.argv[1]
    if not os.path.exists(file_name):
        print(f"File {file_name} does not exist.")
        exit(1)

    metastore_table = config_utils.get_config('config.ini','db_params')['metastore_table']    
    
    ds = load_dataset("parquet", data_files={"train": file_name})
    print(f"Loaded {len(ds['train'])} samples from {file_name}.")
            
    # Connect to the PostgreSQL database
    conn = pg_utils.connect()
    if conn is None:
        print("Error connecting to the database.")
        exit(1)

    # Create a cursor object to execute SQL queries
    cur = conn.cursor()
    
    # Create the metastore table if it does not exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS {metastore_table} (  
        image_uuid UUID PRIMARY KEY,
        image_url TEXT UNIQUE,
        embedding vector(2048),
        metadata_url TEXT,
        original_height INTEGER,
        original_width INTEGER,
        mime_type TEXT,
        has_face BOOLEAN,
        has_glasses BOOLEAN,
        image_download_status BOOLEAN,
        file_name TEXT
    );
    """.format(metastore_table=metastore_table)
    try:
        cur.execute(create_table_query)
        conn.commit()
        print("Table metastore created successfully.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error creating table metastore: {e}")
        
    # Check if the file is already loaded in the table
    check_query = f"SELECT COUNT(*) FROM {metastore_table} WHERE file_name='{file_name}';".format(metastore_table=metastore_table)
    cur.execute(check_query)
    count = cur.fetchone()[0]
    if count > 0:
        print(f"File {file_name} is already loaded in the table. Exiting...")
        cur.close()
        conn.close()
        return
    
    # Iterate through the dataset and insert each record into the database
    try:
        i = 0 
        while i < len(ds['train']):
            j = 0 
            # char_count =  0  
            # postgres_char_limit = 2147483648 / 100  # 2GB limit for PostgreSQL
            values = []
            while i + j < len(ds['train'])  and j < 1000: #and char_count < postgres_char_limit:  # ~200 MB Max limit for each batch
                values.append(cur.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s, %s)", \
                    (str(uuid.uuid4()), ds['train'][i+j]['image_url'], ds['train'][i+j]['embedding'] ,ds['train'][i+j]['metadata_url'], \
                        ds['train'][i+j]['original_height'], ds['train'][i+j]['original_width'], \
                            ds['train'][i+j]['mime_type'], False, file_name)).decode('utf-8'))
                # char_count += len(str(values[i+j]))
                j += 1
            insert_query = f"""
            INSERT INTO {metastore_table} (image_uuid, image_url, embedding, metadata_url, original_height, original_width, \
                mime_type, image_download_status, file_name) 
            VALUES
            """.format(metastore_table=metastore_table)
            # print(f"Insert query: {insert_query}") 
            # print(f"Inserting records {i+1}-{i+j} into the database...")
        
            cur.execute(insert_query + ', '.join(values) + " ON CONFLICT (image_url) DO NOTHING;")
            print(f"Inserted records {i+1}-{i+j} into the database.")
            i += j
        print('Commiting the transaction...')
        conn.commit()
        print('Transaction committed successfully.')
        
    except psycopg2.Error as e:
        print(f"Error inserting records {i+1}-{j+j}: {e}")
        conn.rollback()

    # Perform count query to check the number of records in the metastore table versus the number of records in the dataset
    count_query = f"SELECT COUNT(*) FROM {metastore_table} WHERE file_name='{file_name}';".format(metastore_table=metastore_table)
    if count_query:
        print(f"Count query: {count_query}")
        cur.execute(count_query)
        count = cur.fetchone()[0]
        print(f"Number of records in the metastore table: {count}")
        if count == len(ds['train']):
            print("Counts in table and input file match.")
        else:
            print(f"Number of records in the metastore table does not match the number of records in the dataset. Expected: {len(ds['train'])}, Found: {count}")    

    # Close the cursor and connection
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
import requests 
import pg_utils
import psycopg2
import multiprocessing as mp
import os
from tqdm import tqdm 
import config_utils
            
def update_image_download_status(conn, image_uuid, metastore_table):
    try:
        with conn.cursor() as cursor:
            update_query = "UPDATE " + metastore_table + "SET image_download_status = TRUE WHERE image_uuid = %s;"
            cursor.execute(update_query, (image_uuid,))
            conn.commit()
            return 0
    except psycopg2.Error as e:
        # print(f"Error updating image download status: {e}")
        return -1

# download images from URLs and save them to a local directory
def download_image(row):
    # Check if the file already exists
    # print(f"Downloading image from {url} to {save_path}")
    url = row[1]
    save_path = f"images/{row[0]}.{url.split('.')[-1]}"
    if os.path.exists(save_path):
        # print(f"File {save_path} already exists. Skipping download.")
        return save_path.split('/')[-1].split('.')[0]
    try:
        response = requests.get(url, headers={'User-Agent': 'TakeHomeAssignment/0.0.1'})
        response.raise_for_status()  # Raise an error for bad responses
        with open(save_path, 'wb') as img_file:
            img_file.write(response.content)
        return save_path.split('/')[-1].split('.')[0]
        # print(f"Image saved successfully: {save_path}")
    except requests.RequestException as e:
        # print(f"Error fetching image {url}: {e}")
        return None


def main():
    # Get the image URL from the postgresql database
    conn = pg_utils.connect()
    if conn is None:
        print("Error connecting to the database.")
        exit(1)
        
    conn2 = pg_utils.connect()
    if conn2 is None:
        print("Error connecting to the database.")
        exit(1)
    
    metastore_table = config_utils.get_config('config.ini','db_params')['metastore_table']
    # Multiprocessing pool for parallel processing
    pool = mp.Pool(mp.cpu_count() - 1)
    
    # Fetch data in batches
    query = "SELECT image_uuid, image_url FROM metastore WHERE image_url IS NOT NULL AND NOT image_download_status;"
    
    for batch in pg_utils.fetch_data_in_batches(conn, query):
        results = list(tqdm(pool.imap_unordered(download_image, batch), total=len(batch), desc="Downloading images"))
        for image_uuid in results:
            if image_uuid is not None:
                update_image_download_status(conn2, image_uuid, metastore_table)
    
    conn.close()
    pool.close()
    conn2.close()

if __name__ == "__main__":
    main()
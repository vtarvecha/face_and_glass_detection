import cv2
import pg_utils
import psycopg2
import multiprocessing as mp
from tqdm import tqdm
import config_utils

image_dir = config_utils.get_config('config.ini','image_params')['image_dir']
metastore_table = config_utils.get_config('config.ini','db_params')['metastore_table']

def detect_face_opencv(row):
    image_uuid = row[0]
    image_url = row[1]
    image_extension = image_url.split('.')[-1]
    image_path = f"{image_dir}/{image_uuid}.{image_extension}"
    
    # Load the pre-trained Haar Cascade classifier for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        # print(f"Error: Unable to read image at {image_path}")
        return None

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image with the Haar Cascade classifier if minimum size is 100x100
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
    
    # Return True if faces are detected, otherwise False    
    return True if len(faces) > 0 else False

def update_face_detection_status(conn, image_uuid, has_face):
    try:
        with conn.cursor() as cursor:
            update_query = """
            UPDATE {metastore_table} 
            SET has_face = %s 
            WHERE image_uuid = %s;
            """
            cursor.execute(update_query, (has_face, image_uuid))
            conn.commit()
            return 0
    except psycopg2.Error as e:
        print(f"Error updating face detection status: {e}")
        return -1
    
def main():
    # Example usage
    conn = pg_utils.connect()
    if conn is None:
        print("Error connecting to the database.")
        exit(1)
    
    # Multiprocessing pool for parallel processing
    pool = mp.Pool(mp.cpu_count() - 1)
    
    # Scan PostgreSQL database to get the image URLs and metadata
    query = f"SELECT image_uuid, image_url FROM {metastore_table} WHERE has_face IS NULL;"
        
    for batch in pg_utils.fetch_data_in_batches(conn, query):
        results = list(tqdm(pool.imap_unordered(detect_face_opencv, batch), total=len(batch), desc="Detecting faces"))
        conn2 = pg_utils.connect()
        for image_uuid, has_face in zip(batch, results):
            if has_face is not None:
                # Update the face detection status in the database
                update_face_detection_status(conn2, image_uuid[0], has_face)
                # print(f"Updated face detection status for image UUID {image_uuid[0]}: {has_face}")
            
    # Close the connection to the database
    conn.close()        
if __name__ == "__main__":
    main()
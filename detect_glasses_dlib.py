import numpy as np
import dlib 
import cv2 
from PIL import Image 
import statistics 
import pg_utils
from tqdm import tqdm
import psycopg2
import multiprocessing as mp
import os


# Global variables
data_directory = pg_utils.get_config('config.ini','local')['data_directory']
metastore_table = pg_utils.get_config('config.ini','db_params')['metastore_table']
image_dir = pg_utils.get_config('config.ini','local')['image_dir']
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(f"{data_directory}/shape_predictor_68_face_landmarks.dat")


def glasses_detector(row):
    image_uuid = row[0]
    image_url = row[1]
    image_extension = image_url.split('.')[-1]
    image = f"{image_dir}/{image_uuid}.{image_extension}"
    try:
        img = dlib.load_rgb_image(image)
    except Exception as e:
        # print(f"Error loading image {image}: {e}")
        return False
    
    if len(detector(img)) == 0:
        return False
    
    rect  = detector(img)[0]
    shape = predictor(img, rect)
    landmarks = np.array([[p.x, p.y] for p in shape.parts()])
    
    nose_bridge_x = []
    nose_bridge_y = []
    
    for i in range(28, 36):
        nose_bridge_x.append(landmarks[i][0])
        nose_bridge_y.append(landmarks[i][1]) 
    
    x_min = int(min(nose_bridge_x))
    x_max = int(max(nose_bridge_x))
    y_min = landmarks[20][1]
    y_max = landmarks[30][1]
    
    img2 = Image.open(image)
    img2 = img2.crop((x_min, y_min, x_max, y_max))
    
    img_blur = cv2.GaussianBlur(np.array(img2), (3, 3), sigmaX=0, sigmaY=0) 
    
    edges = cv2.Canny(img_blur, 100, 200)
    edges_center = edges.T[int(len(edges.T) / 2)]
    
    if 255 in edges_center:
        return True
    else:
        return False

def update_glass_detection_status(conn, image_uuid, has_face):
    try:
        with conn.cursor() as cursor:
            update_query = """
            UPDATE %s 
            SET has_glasses = %s 
            WHERE image_uuid = %s;
            """
            cursor.execute(update_query, (metastore_table, has_face, image_uuid))
            conn.commit()
            return 0
    except psycopg2.Error as e:
        print(f"Error updating glass detection status: {e}")
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
    query = f"SELECT image_uuid, image_url FROM {metastore_table} WHERE has_face AND has_glasses IS NULL;"
        
    for batch in pg_utils.fetch_data_in_batches(conn, query):
        results = list(tqdm(pool.imap_unordered(glasses_detector, batch), total=len(batch), desc="Detecting faces"))
        conn2 = pg_utils.connect()
        for image_uuid, has_glasses in zip(batch, results):
            if has_glasses is not None:
                # Update the face detection status in the database
                update_glass_detection_status(conn2, image_uuid[0], has_glasses)
                # print(f"Updated face detection status for image UUID {image_uuid[0]}: {has_face}")
            
    # Close the connection to the database
    conn.close()        


if __name__ == "__main__":
    main()
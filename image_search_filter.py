import pg_utils 
import config_utils

# Global variables
metastore_table = config_utils.get_config('config.ini','db_params')['metastore_table']


def generate_html_response(filter):
    filter = filter.lower()
    if filter == 'with_face':
        query_string = f"SELECT image_uuid, image_url FROM {metastore_table} WHERE has_face AND image_url IS NOT NULL LIMIT 300;"
    elif filter == 'with_glasses':
        query_string = f"SELECT image_uuid, image_url FROM {metastore_table} WHERE has_glasses AND image_url IS NOT NULL LIMIT 300;"
    else:
        query_string = f"SELECT image_uuid, image_url FROM {metastore_table} WHERE image_url IS NOT NULL LIMIT 300;"
    
    response = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Image Search</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                }
                .image-container {
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                }
                .image-container img {
                    margin: 10px;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                }
                .image-container img:hover {
                    transform: scale(1.05);
                    transition: transform 0.2s;
                }
                </style>
                </head>
                <body>
                <h1>Image Search Results</h1>
                <div class="image-container">
                """
    
    with pg_utils.connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query_string)
            rows = cursor.fetchall()
            images = [f"<img src='/images/{row[0]}.{row[1].split('.')[-1]}'  style='width:25%'>" for row in rows]
            images_html = "\n".join(images)
    
    response += images_html
            
    response += """
                </div>
                </body>
                </html>
                """
    return response
def main():
    filter = 'with_face'  # Example filter, can be 'with_face', 'with_glasses', or any other filter
    html_response = generate_html_response(filter)
    print(html_response)  # For testing purposes, you can print the HTML response or save it to a file

if __name__ == "__main__":
    main()


from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import config_utils
from pydantic import BaseModel
import image_search_filter

#Global variables
image_dir = config_utils.get_config('config.ini','local')['image_dir']

app = FastAPI() 
app.mount("/images", StaticFiles(directory=image_dir), name="images")

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Image Search</title>
        </head>
        <body>
            <h1>Image Search</h1>
            <form action="/search" method="get">
                # Filter by All, with face, or with glasses
                <label for="filter">Filter:</label>
                <select name="filter" id="filter">
                    <option value="all">All</option>
                    <option value="with_face">With Face</option>
                    <option value="with_glasses">With Glasses</option>
                </select>
                <br><br>
                <input type="submit" value="filter">
            </form>
        </body>
    </html>
    """
    
    
@app.get("/search", response_class=HTMLResponse)
def search_images(filter: str):
    # Here you would implement the logic to search for images based on the query.
    # For demonstration, we'll just return a simple HTML response.
    
    return image_search_filter.generate_html_response(filter)
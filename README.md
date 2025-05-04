# image_classification
Project to build a pipeline that sources Image dataset from Hugging Face, runs it through Image Object Detection model, and stores it in user friendly way that enables downstream users to search for images based on search criteria. 


Project Structure
image_classification/
│
├── config.ini                        # Configuration file
├── config_utils.py                   # Configuration utilities script. 
├── pg_utils.py                       # Utilities for PostgreSQL operations
├── download_files_to_local.py        # Downloads Hugging Face Dataset files to local
├── ingestion.py                      # Create and ingests data into PostgreSQL metastore. 
├── download_images.py                # Downloads images to local
├── detect_face_opencv.py             # Runs all images through OpenCV to detect faces. 
├── detect_glasses_dlib.py            # Runs all images through DLib based algorithm to detect glasses. 
├── image_search.py                   # Python FastAPI to perform image search. 
├── image_search_filter.py            # Utilities function to generate Python response based on filter conditions. 
├── LICENSE                           # License File. 
└── README.md                         # Project documentation


🚀 Getting Started
1. Clone the Repository

git clone https://github.com/vtarvecha/image_classification.git
cd image_classification

2. Set Up the Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Data preparation Steps

   3.1 Setup configuration files config.ini per example provided and description below.
   
   |--------------|---------------------|-----------------------------------------------|
   |    Section   |   Parameter         |                 Description                   |
   |--------------|---------------------|-----------------------------------------------|
   | local        | data_directory      | Local directory to store files                |
   | local        | image_dir           | Local directory to store images               |
   | db_params    | metastore_table     | Postgres table name to use as meta store      |
   | posgresql    | host                | PostgreSQL server host name                   |
   | postgresql   | database            | PostgreSQL database name                      |
   | postgresql   | port                | PostgreSQL port                               |
   | postgresql   | user                | PostgreSQL user name                          |
   | postgresql   | password            | PostgreSQL password                           |
   |--------------|---------------------|-----------------------------------------------|

   3.2 Download files to local
   pthon download_files_to_local.py

   3.3 Ingestion ( For each file download ) 
   python ingestion.py <file_name>

   3.4 Download Images
   python download_images.py

   3.5 Run Face detection
   python detect_face_opencv.py

   3.6 Run Glasses detection
   python detect_glasses_dlib.py

4. Stand up Search API
   fastapi run image_search.py
   
   

import configparser
import os

def get_config(filename, section):
    """Read the configuration file and return the parameters for the specified section."""
    #Check if the file exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"The configuration file {filename} does not exist.")
    parser = configparser.ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section', section, 'not found in the', filename, 'file')
    return db

def main():
    # Example usage
    try:
        db_params = get_config('database.ini', 'postgresql')
        print("Database parameters:", db_params)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
        
if __name__ == "__main__":
    main()
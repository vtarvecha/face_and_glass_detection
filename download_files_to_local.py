from huggingface_hub import hf_hub_download
import config_utils

def download_file_from_huggingface(repo_id, filename, local_dir):
    """Download a file from Hugging Face Hub and save it to a local directory."""
    try:
        download_file = hf_hub_download(repo_id=repo_id, filename=filename, local_dir=local_dir)
        print(f"Downloaded {filename} to {local_dir}.")
        return download_file 
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return None

def main():
    NUMBER_OF_SPLITS = 330
    SPLITS_TO_READ = 2
    for i in range(SPLITS_TO_READ):
        repo_id = "wikimedia/wit_base" 
        directory_name = config_utils.get_config('config.ini', 'local')['data_directory']
        download_file_from_huggingface(repo_id=repo_id, filename=f"train-{i:05d}-of-{NUMBER_OF_SPLITS:05d}.parquet", local_dir=directory_name)

if __name__ == "__main__":
    main()
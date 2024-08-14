import csv
import os
import requests
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# AWS S3 configuration
AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''
AWS_REGION = 'us-east-2'  # Replace with your AWS region
S3_BUCKET_NAME = 'mbtadata'

# Local directory to store downloaded files temporarily
TEMP_DIR = 'mbta_data_temp'

# Create a session using your credentials
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

# Create an S3 resource
s3 = session.resource('s3')
bucket = s3.Bucket(S3_BUCKET_NAME)

def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def upload_to_s3(local_file, s3_key):
    try:
        bucket.upload_file(local_file, s3_key)
        print(f"Successfully uploaded {local_file} to {s3_key}")
    except ClientError as e:
        print(f"Failed to upload {local_file} to {s3_key}: {str(e)}")
        raise

def process_file(row):
    service_date = datetime.strptime(row['service_date'], '%Y-%m-%d')
    file_url = row['file_url']
    filename = os.path.basename(file_url)
    local_file = os.path.join(TEMP_DIR, filename)

    try:
        print(f"Downloading {filename}")
        download_file(file_url, local_file)

        print(f"Uploading {filename} to S3")
        s3_key = f"mbta_data/{service_date.year}/{service_date.month:02d}/{service_date.day:02d}/{filename}"
        upload_to_s3(local_file, s3_key)

        print(f"Successfully processed {filename}")
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
    finally:
        if os.path.exists(local_file):
            os.remove(local_file)

def main():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    with open('/Users/yashvardhansinghranawat/Documents/MBTA_ETL_Pipeline/data/index_file/mbta_performance_index_20240811_022957.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_file, row) for row in reader]
            
            for future in as_completed(futures):
                future.result()

    print("All files processed")

if __name__ == "__main__":
    main()
import boto3
import os
from botocore.config import Config

# Fetch environment variables
'''
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
'''

S3_BUCKET_NAME='mbtadata'
S3_FOLDER='s3://mbtadata/index_file/'
AWS_ACCESS_KEY=''
AWS_SECRET_KEY = ''
AWS_REGION = 'us-east-2'

def upload_file_to_s3(file_path):
    try:
        # Create a session using your credentials
        session = boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )

        # Create an S3 client with explicit signature version
        s3 = session.client('s3', config=Config(signature_version='s3v4'))

        # Extract the filename from the file path
        filename = os.path.basename(file_path)

        # Upload the content to S3
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=f"index_file/{filename}",
            Body=open(file_path, 'rb'),
            ContentType='text/csv'
        )

        print(f"File uploaded successfully to s3://{S3_BUCKET_NAME}/mbta_data/{filename}")

    except Exception as e:
        print(f"Error uploading to S3: {e}")

if __name__ == "__main__":
    # Replace 'your_file.csv' with the actual filename returned from the download script
    upload_file_to_s3('/Users/yashvardhansinghranawat/Documents/MBTA_ETL_Pipeline/data/index_file/mbta_performance_index_20240811_022957.csv')

import requests
from datetime import datetime

# URL of the index file
INDEX_URL = "https://performancedata.mbta.com/lamp/subway-on-time-performance-v1/index.csv"

def download_file(url):
    try:
        # Fetch the file from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Generate a filename with the current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mbta_performance_index_{timestamp}.csv"

        # Save the file locally
        with open("/Users/yashvardhansinghranawat/Documents/MBTA_ETL_Pipeline/data/index_file/"+filename, 'wb') as file:
            file.write(response.content)

        print(f"File downloaded successfully as {filename}")
        return filename

    except requests.RequestException as e:
        print(f"Error downloading the file: {e}")
        return None

if __name__ == "__main__":
    download_file(INDEX_URL)
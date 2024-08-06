import requests
from bs4 import BeautifulSoup
import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# URL of the website to scrape
URL = 'https://portal.ct.gov/dss/archived-folder/temporary-family-assistance---tfa'

# Send a GET request to the website
response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

# Define block to scrape
block_class = 'content'

# Extract the content from the specified block
content_div = soup.find('div', class_=block_class)
if content_div:
    text = content_div.get_text(strip=True)
else:
    text = 'Content not found.'

# Convert data to JSON format
data = {
    'content': text
}
json_data = json.dumps(data, ensure_ascii=False, indent=4)

# Save JSON data to a file with UTF-8 encoding
with open('temporary_family_assistance.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)

# AWS S3 configuration
s3_bucket_name = 'beacon-database'
s3_file_name = 'temporary_family_assistance.json'

# Initialize the S3 client
s3 = boto3.client('s3', region_name='us-east-1')
s3.delete_object(Bucket=s3_bucket_name, Key=s3_file_name)

try:
    # Upload JSON file to S3
    s3.upload_file('temporary_family_assistance.json', s3_bucket_name, s3_file_name)
    print("Data uploaded to S3 successfully")
except FileNotFoundError:
    print("The file was not found")
except NoCredentialsError:
    print("Credentials not available")
except PartialCredentialsError:
    print("Incomplete credentials provided")
except boto3.exceptions.S3UploadFailedError as e:
    print(f"Failed to upload: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Optional: Remove the local JSON file after upload
import os
os.remove('temporary_family_assistance.json')

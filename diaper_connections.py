import requests
from bs4 import BeautifulSoup
import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# URL of the website to scrape
URL = 'https://www.thediaperbank.org/diaper-connections/'

# Send a GET request to the website
response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

# Define blocks to scrape
blocks = [
    {'class': 'et_pb_column et_pb_column_2_3 et_pb_column_1 et_pb_css_mix_blend_mode_passthrough et-last-child'},
    {'class': 'et_pb_column et_pb_column_2_3 et_pb_column_2 et_pb_css_mix_blend_mode_passthrough'},
    {'class': 'et_pb_column et_pb_column_2_3 et_pb_column_5 et_pb_css_mix_blend_mode_passthrough et-last-child'}
]

documents = []

for block in blocks:
    for div in soup.find_all('div', class_=block['class']):
        # Extracting text from the div
        text = div.get_text(strip=True)
        # Adding text to the documents list
        documents.append({'text': text})

# Convert documents to JSON format
json_data = json.dumps(documents, ensure_ascii=False, indent=4)

# Save JSON data to a file with UTF-8 encoding
with open('diaper_connections.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)

# AWS S3 configuration
s3_bucket_name = 'beacon-database'
s3_file_name = 'diaper_connections.json'

# Initialize the S3 client
s3 = boto3.client('s3', region_name='us-east-1')
s3.delete_object(Bucket=s3_bucket_name, Key=s3_file_name)

try:
    # Upload JSON file to S3
    s3.upload_file('diaper_connections.json', s3_bucket_name, s3_file_name)
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

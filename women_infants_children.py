import requests
from bs4 import BeautifulSoup
import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# URL of the webpage to scrape
url = 'https://portal.ct.gov/dph/wic/wic'

# Send a GET request to the website
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract data
data = []

# Define the styles to target
target_styles = [
    'margin: 0in 0in 0pt;',
    'text-align: left;'
]

# Find and extract <p> and <div> tags with the specified styles
for style in target_styles:
    for tag in soup.find_all(['p', 'div'], style=style):
        text_content = tag.get_text(strip=True)
        data.append({
            'tag': tag.name,
            'style': style,
            'content': text_content
        })

# Convert data to JSON format
json_data = json.dumps(data, ensure_ascii=False, indent=4)

# Save JSON data to a file with UTF-8 encoding
with open('women_infants_children.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)

# AWS S3 configuration
s3_bucket_name = 'beacon-database'
s3_file_name = 'women_infants_children.json'

# Initialize the S3 client
s3 = boto3.client('s3', region_name='us-east-1')
s3.delete_object(Bucket=s3_bucket_name, Key=s3_file_name)

try:
    # Upload JSON file to S3
    s3.upload_file('women_infants_children.json', s3_bucket_name, s3_file_name)
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
os.remove('women_infants_children.json')

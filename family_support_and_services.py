import requests
from bs4 import BeautifulSoup
import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Fetch the webpage content
url = "https://portal.ct.gov/dds/supports-and-services/family-support-and-services?language=en_US"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract data
data = []

# Find all divs with the specified class
for div in soup.find_all('div', class_='cg-c-lead-story__body col'):
    block_content = div.get_text(strip=True, separator=' ')
    list_items = [li.get_text(strip=True) for li in div.find_all('li')]
    
    # Combine the block content with list items
    combined_content = {
        'block_content': block_content,
        'list_items': list_items
    }
    data.append(combined_content)

# Convert data to JSON format
json_data = json.dumps(data, ensure_ascii=False, indent=4)

# Save JSON data to a file with UTF-8 encoding
json_file_path = 'family_support_and_services.json'
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)

# AWS S3 configuration
s3_bucket_name = 'beacon-database'
s3_file_name = 'family_support_and_services.json'

# Initialize the S3 client
s3 = boto3.client('s3', region_name='us-east-1')
s3.delete_object(Bucket=s3_bucket_name, Key=s3_file_name)

try:
    # Upload JSON file to S3
    s3.upload_file(json_file_path, s3_bucket_name, s3_file_name)
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

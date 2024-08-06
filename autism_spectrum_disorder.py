import requests
from bs4 import BeautifulSoup
import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Fetch the webpage content
url = 'https://www.connecticutchildrens.org/specialties-conditions/developmental-behavioral-pediatrics/autism-spectrum-disorder-asd'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract data
data = []

# Function to clean the text content
def clean_text(text):
    return text  # No need to decode explicitly

# Find and extract all <p> tags
for tag in soup.find_all(['p']):
    text_content = clean_text(tag.get_text(strip=True))
    data.append({
        'tag': tag.name,
        'content': text_content
    })

# Convert data to JSON format
json_data = json.dumps(data, ensure_ascii=False, indent=4)

# Save JSON data to a file with UTF-8 encoding
with open('autism_spectrum_disorder.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)

# AWS S3 configuration
s3_bucket_name = 'beacon-database'
s3_file_name = 'autism_spectrum_disorder.json'

# Initialize the S3 client
s3 = boto3.client('s3', region_name='us-east-1')
s3.delete_object(Bucket=s3_bucket_name, Key=s3_file_name)

try:
    # Upload JSON file to S3
    s3.upload_file('autism_spectrum_disorder.json', s3_bucket_name, s3_file_name)
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

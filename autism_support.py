import requests
from bs4 import BeautifulSoup
import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Step 1: Fetch the web page
url = 'https://www.healthline.com/health/autism#support'
response = requests.get(url)
html_content = response.text

# Step 2: Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Example: Extract the title and any support sections
data = []
divs = soup.find_all('div', class_='css-1avyp1d')

for div in divs:
    div_content = div.get_text(strip=True)
    data.append({
        'content': div_content
    })

# Convert data to JSON format
data_json = json.dumps(data, ensure_ascii=False)

# Step 3: Upload data to AWS S3
s3_bucket_name = 'beacon-database'
s3_key = 'autism_support.json'

# Initialize Boto3 S3 client
s3_client = boto3.client('s3')
s3_client.delete_object(Bucket=s3_bucket_name, Key=s3_key)

# Upload data to S3
try:
    s3_client.put_object(Bucket=s3_bucket_name, Key=s3_key, Body=data_json)
    print("Data successfully uploaded to S3")
except (NoCredentialsError, PartialCredentialsError) as e:
    print(f"Credentials error: {e}")
except Exception as e:
    print(f"Error uploading data to S3: {e}")

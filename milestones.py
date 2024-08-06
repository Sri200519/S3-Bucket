import requests
from bs4 import BeautifulSoup
import json
import boto3

# Step 1: Fetch the web page
url = 'https://kidshealth.org/en/parents/milestones.html'
response = requests.get(url)
html_content = response.text

# Step 2: Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find all div elements with the class 'cmp-container'
data = []
divs = soup.find_all('div', class_='cmp-container')

for div in divs:
    div_content = div.get_text(strip=True)
    data.append({
        'content': div_content
    })

# Convert data to JSON format
data_json = json.dumps(data, ensure_ascii=False)

# AWS S3 Configuration
s3_bucket_name = 'beacon-database'
s3_key = 'milestones.json'

# Initialize Boto3 S3 client
s3_client = boto3.client('s3')
s3_client.delete_object(Bucket=s3_bucket_name, Key=s3_key)

# Upload data to S3
try:
    s3_client.put_object(Bucket=s3_bucket_name, Key=s3_key, Body=data_json)
    print("Data successfully uploaded to S3")
except Exception as e:
    print(f"Error uploading data to S3: {e}")

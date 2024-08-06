import requests
from bs4 import BeautifulSoup
import boto3
import json

# Step 1: Fetch the web page
url = 'https://autism.org/what-is-autism/'
response = requests.get(url)
html_content = response.text

# Step 2: Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find all div elements with the specified classes
data = []
divs1 = soup.find_all('div', class_='fusion-text fusion-text-1')
divs2 = soup.find_all('div', class_='fusion-text fusion-text-2')

# Extract content from the first class
for div in divs1:
    div_content = div.get_text(strip=True)
    data.append({
        'class': 'fusion-text-1',
        'content': div_content
    })

# Extract content from the second class
for div in divs2:
    div_content = div.get_text(strip=True)
    data.append({
        'class': 'fusion-text-2',
        'content': div_content
    })

# Convert data to JSON format
data_json = json.dumps(data, ensure_ascii=False)

# AWS S3 Configuration
s3_bucket_name = 'beacon-database'  # Replace with your S3 bucket name
s3_key = 'autism_info.json'  # The key under which the data will be stored

# Initialize Boto3 S3 client
s3_client = boto3.client('s3')
s3_client.delete_object(Bucket=s3_bucket_name, Key=s3_key)

# Upload data to S3
try:
    s3_client.put_object(Bucket=s3_bucket_name, Key=s3_key, Body=data_json)
    print("Data successfully uploaded to S3")
except Exception as e:
    print(f"Error uploading data to S3: {e}")

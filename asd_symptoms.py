import requests
from bs4 import BeautifulSoup
import boto3
import json

# Step 1: Fetch the web page
url = 'https://www.mayoclinic.org/diseases-conditions/autism-spectrum-disorder/symptoms-causes/syc-20352928'
response = requests.get(url)
html_content = response.text

# Step 2: Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find the contentbox div
contentbox_div = soup.find('div', class_='contentbox')

# Initialize an empty list to store data
data = []

# Only proceed if the contentbox_div is found
if contentbox_div:
    # Start from the next sibling of contentbox_div
    for div in contentbox_div.find_all_next('div', recursive=False):
        # Break if a div with class 'requestappt' is encountered
        if 'requestappt' in div.get('class', []):
            break

        # Extract content from p, h2, h3, and ul tags within the div
        for tag in div.find_all(['p', 'h2', 'h3', 'ul']):
            tag_name = tag.name
            tag_content = tag.get_text(strip=True)
            
            # Handle lists separately
            if tag_name == 'ul':
                list_items = [li.get_text(strip=True) for li in tag.find_all('li')]
                tag_content = '\n'.join(list_items)
            
            data.append({
                'tag': tag_name,
                'content': tag_content
            })

# Step 3: Convert data to JSON format
data_json = json.dumps(data, ensure_ascii=False)

# Step 4: AWS S3 Configuration
s3_bucket_name = 'beacon-database'
s3_key = 'asd_symptoms.json'

# Initialize Boto3 S3 client
s3_client = boto3.client('s3')
s3_client.delete_object(Bucket=s3_bucket_name, Key=s3_key)

# Upload data to S3
try:
    s3_client.put_object(Bucket=s3_bucket_name, Key=s3_key, Body=data_json)
    print("Data successfully uploaded to S3")
except Exception as e:
    print(f"Error uploading data to S3: {e}")

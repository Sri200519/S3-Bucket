import requests
from bs4 import BeautifulSoup
import boto3
import json

# Fetch the web page
url = 'https://www.autismspeaks.org/signs-autism'
response = requests.get(url)
html_content = response.text

# Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find the specific div by class
target_divs = soup.find_all('div', class_='basic-block')

# Extract content from p, h2, h3, ul, and a tags within the specific divs
data = []
for target_div in target_divs:
    section_data = []
    for tag in target_div.find_all(['p', 'h2', 'h3', 'ul', 'a']):
        tag_name = tag.name
        if tag_name == 'a':
            tag_content = tag.get_text(strip=True)
            href = tag.get('href', '')
            section_data.append({
                'tag': tag_name,
                'content': tag_content,
                'href': href
            })
        else:
            tag_content = tag.get_text(strip=True)
            if tag_name == 'ul':
                list_items = [li.get_text(strip=True) for li in tag.find_all('li')]
                tag_content = '\n'.join(list_items)
            section_data.append({
                'tag': tag_name,
                'content': tag_content
            })
    if section_data:
        data.append(section_data)

# Debugging: Print the length and content of the data list
print(f"Number of sections extracted: {len(data)}")
print("Data extracted:")
for section in data:
    print(section)

# Convert data to JSON format
data_json = json.dumps(data, ensure_ascii=False)

# AWS S3 Configuration
s3_bucket_name = 'beacon-database'  # Replace with your S3 bucket name
s3_key = 'signs_autism.json'  # The key (path) under which the file will be stored in the bucket

# Initialize Boto3 S3 client
s3_client = boto3.client('s3')
s3_client.delete_object(Bucket=s3_bucket_name, Key=s3_key)

# Upload data to S3
try:
    s3_client.put_object(Bucket=s3_bucket_name, Key=s3_key, Body=data_json)
    print("Data successfully uploaded to S3")
except Exception as e:
    print(f"Error uploading data to S3: {e}")

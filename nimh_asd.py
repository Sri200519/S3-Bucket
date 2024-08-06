import requests
from bs4 import BeautifulSoup
import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Fetch the web page
url = 'https://www.nimh.nih.gov/health/topics/autism-spectrum-disorders-asd'
response = requests.get(url)
html_content = response.text

# Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find the specific div by ID and class
target_div = soup.find('div', id='main_content', class_='areanav-true sidebar-true')

# Extract content from p, h2, h3, ul, and a tags within the specific div
data = []
if target_div:
    for tag in target_div.find_all(['p', 'h2', 'h3', 'ul', 'a']):
        tag_name = tag.name
        if tag_name == 'a':
            tag_content = tag.get_text(strip=True)
            href = tag.get('href', '')
            data.append({
                'tag': tag_name,
                'content': tag_content,
                'href': href
            })
        else:
            tag_content = tag.get_text(strip=True)
            if tag_name == 'ul':
                list_items = [li.get_text(strip=True) for li in tag.find_all('li')]
                tag_content = '\n'.join(list_items)
            data.append({
                'tag': tag_name,
                'content': tag_content
            })
else:
    print("Target div not found")

# Debugging: Print the length and content of the data list
print(f"Number of items extracted: {len(data)}")
print("Data extracted:")
for item in data:
    print(item)

# Convert data to JSON format
data_json = json.dumps(data, ensure_ascii=False)

# AWS S3 Configuration
s3_bucket_name = 'beacon-database'  # Replace with your bucket name
s3_key = 'nimh_asd.json'  # Replace with the desired S3 object key

# Initialize Boto3 S3 client
s3_client = boto3.client('s3')
s3_client.delete_object(Bucket=s3_bucket_name, Key=s3_key)

# Upload data to S3
try:
    s3_client.put_object(Bucket=s3_bucket_name, Key=s3_key, Body=data_json)
    print("Data successfully uploaded to S3")
except NoCredentialsError:
    print("AWS credentials not found. Please configure your AWS credentials.")
except PartialCredentialsError:
    print("Incomplete AWS credentials. Please check your AWS credentials.")
except Exception as e:
    print(f"Error uploading data to S3: {e}")

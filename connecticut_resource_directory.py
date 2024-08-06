import requests
from bs4 import BeautifulSoup
import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Fetch the webpage content
url = 'https://portal.ct.gov/oca/miscellaneous/miscellaneous/resources/resource-list'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Initialize data list
data = []

# Function to parse items and descriptions from the siblings
def parse_items_and_descriptions(start_ul):
    items = []
    descriptions = []
    ul = start_ul

    while ul:
        for li in ul.find_all('li'):
            link = li.find('a')
            link_text = link.get_text(strip=True) if link else ''
            link_href = link['href'] if link else ''
            items.append({
                'text': link_text,
                'href': link_href
            })
        
        # Find the next description <p> tag
        next_p = ul.find_next_sibling('p', style='text-align: justify;')
        if next_p:
            descriptions.append(next_p.get_text(strip=True))
        
        # Move to the next <ul> if it exists
        ul = next_p.find_next_sibling('ul', style='list-style-type: disc;') if next_p else None

    return items, descriptions

# Extract data
heading = None
for tag in soup.find_all(['p', 'ul']):
    if tag.name == 'p' and 'margin-bottom: 0in;' in tag.get('style', ''):
        if heading:
            # Save previous heading's data before starting a new one
            data.append({
                'title': heading['title'],
                'items': heading['items'],
                'descriptions': heading['descriptions']
            })

        # Start a new heading
        heading = {
            'title': tag.get_text(strip=True),
            'items': [],
            'descriptions': []
        }

        # Parse items and descriptions starting from the next sibling <ul>
        next_ul = tag.find_next_sibling('ul', style='list-style-type: disc;')
        if next_ul:
            heading['items'], heading['descriptions'] = parse_items_and_descriptions(next_ul)
    
# Append the last heading
if heading:
    data.append({
        'title': heading['title'],
        'items': heading['items'],
        'descriptions': heading['descriptions']
    })

# Convert data to JSON format
json_data = json.dumps(data, ensure_ascii=False, indent=4)

# Save JSON data to a file with UTF-8 encoding
with open('connecticut_resource_directory.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)

# AWS S3 configuration
s3_bucket_name = 'beacon-database'
s3_file_name = 'connecticut_resource_directory.json'

# Initialize the S3 client
s3 = boto3.client('s3', region_name='us-east-1')
s3.delete_object(Bucket=s3_bucket_name, Key=s3_file_name)

try:
    # Upload JSON file to S3
    s3.upload_file('connecticut_resource_directory.json', s3_bucket_name, s3_file_name)
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

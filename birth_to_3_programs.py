import requests
from bs4 import BeautifulSoup
import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# List of URLs to scrape
URLs = [
    'https://www.birth23.org/programs/?town&program_type',
    'https://www.birth23.org/programs/page/2/?town&program_type'
]

# Define User-Agent string
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def extract_program_info(div):
    """Extract program information from a div block."""
    title = div.find('h3').get_text(strip=True) if div.find('h3') else 'No Title'
    category = div.find('div', class_='program-block-categories').get_text(strip=True) if div.find('div', class_='program-block-categories') else 'No Category'
    
    # Extract contact email
    contact_div = div.find('div', class_='program-block-contact')
    contact_email = 'No Contact Email'
    if contact_div:
        email_link = contact_div.find('a')
        if email_link and 'href' in email_link.attrs:
            contact_email = email_link.attrs['href'].replace('mailto:', '')
        else:
            contact_email = contact_div.get_text(strip=True)
    
    # Extract phone number
    phone_number = div.find('div', class_='program-block-phone').get_text(strip=True) if div.find('div', class_='program-block-phone') else 'No Phone Number'
    
    return {
        'title': title,
        'category': category,
        'contact_email': contact_email,
        'phone_number': phone_number
    }

# Data extraction
all_programs = []

# Iterate over each URL
for URL in URLs:
    print(f'Scraping {URL}')
    try:
        response = requests.get(URL, headers=HEADERS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Print the page title for debugging
            print(f'Page Title: {soup.title.string}')

            # Define block to scrape
            blocks = soup.find_all('div', class_='loop-program program-block program-post')

            # Check if any blocks are found
            if not blocks:
                print(f'No blocks found on {URL}.')
                continue

            # Extract data
            for block in blocks:
                program_info = extract_program_info(block)
                all_programs.append(program_info)

            print(f'Data extracted from {URL}.')
        else:
            print(f'Failed to retrieve {URL} with status code: {response.status_code}')
    except Exception as e:
        print(f'An error occurred while scraping {URL}: {e}')

# Convert data to JSON format
json_data = json.dumps(all_programs, ensure_ascii=False, indent=4)

# Save JSON data to a file with UTF-8 encoding
json_file_name = 'birth_to_3_programs.json'
with open(json_file_name, 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)

# AWS S3 configuration
s3_bucket_name = 'beacon-database'
s3_file_name = json_file_name

# Initialize the S3 client
s3 = boto3.client('s3', region_name='us-east-1')
s3.delete_object(Bucket=s3_bucket_name, Key=s3_file_name)

try:
    # Upload JSON file to S3
    s3.upload_file(json_file_name, s3_bucket_name, s3_file_name)
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
os.remove(json_file_name)

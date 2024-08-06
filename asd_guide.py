import time
import boto3
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Fetch the web page
url = 'https://childmind.org/guide/autism-spectrum-disorder-quick-guide/'
driver.get(url)

# Wait for the content to load (adjust time if necessary)
time.sleep(5)

# Get page source and parse with BeautifulSoup
html_content = driver.page_source
soup = BeautifulSoup(html_content, 'html.parser')

# Find the specific div by class
target_div = soup.find('div', class_='w-full mt-16 md:px-3 md:row-span-2 xl:row-span-1')

# Extract content from p, h2, h3, and ul tags within the specific div
data = []
if target_div:
    for tag in target_div.find_all(['p', 'h2', 'h3', 'ul']):
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
else:
    print("Target div not found")

# Debugging: Print the length and content of the data list
print(f"Number of items extracted: {len(data)}")
print("Data extracted:")
for item in data:
    print(item)

# Close the WebDriver
driver.quit()

# Convert data to JSON format
data_json = json.dumps(data, ensure_ascii=False)

# AWS S3 Configuration
s3_bucket_name = 'beacon-database'
s3_key = 'asd_guide.json'

# Initialize Boto3 S3 client
s3_client = boto3.client('s3',region_name='us-east-1')

s3_client.delete_object(Bucket=s3_bucket_name, Key=s3_key)

# Upload data to S3
try:
    s3_client.put_object(Bucket=s3_bucket_name, Key=s3_key, Body=data_json)
    print("Data successfully uploaded to S3")
except Exception as e:
    print(f"Error uploading data to S3: {e}")

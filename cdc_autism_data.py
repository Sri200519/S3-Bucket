import requests
from bs4 import BeautifulSoup
import json
import boto3

# Fetch the web page
url = 'https://www.cdc.gov/autism/data-research/?CDC_AAref_Val=https://www.cdc.gov/ncbddd/autism/data.html'
response = requests.get(url)
html_content = response.text

# Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Function to extract text content from a given div section
def extract_text_content(section_div):
    content = []
    for tag in section_div.find_all(['p', 'h2', 'h3', 'ul', 'a']):
        tag_name = tag.name
        if tag_name == 'a':
            tag_content = tag.get_text(strip=True)
            href = tag.get('href', '')
            content.append({
                'tag': tag_name,
                'content': tag_content,
                'href': href
            })
        else:
            tag_content = tag.get_text(strip=True)
            if tag_name == 'ul':
                list_items = [li.get_text(strip=True) for li in tag.find_all('li')]
                tag_content = '\n'.join(list_items)
            content.append({
                'tag': tag_name,
                'content': tag_content
            })
    return content

# Function to extract table data from a given div section
def extract_table_content(section_div):
    table_data = []
    table = section_div.find('table')
    if table:
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        for row in table.find_all('tr')[1:]:  # Skip the header row
            columns = row.find_all('td')
            if len(columns) > 0:
                row_data = {}
                for i, column in enumerate(columns):
                    row_data[headers[i]] = column.get_text(strip=True)
                table_data.append(row_data)
    return table_data

# Find and extract data from the specified sections
data = []
section1_div = soup.find('div', class_='dfe-section', attrs={'data-section': 'cdc_data_surveillance_section_1'})
if section1_div:
    section1_content = extract_text_content(section1_div)
    data.append({
        'section': 'cdc_data_surveillance_section_1',
        'content': section1_content
    })

section2_div = soup.find('div', class_='dfe-section', attrs={'data-section': 'cdc_data_surveillance_section_2'})
if section2_div:
    section2_content = extract_table_content(section2_div)
    data.append({
        'section': 'cdc_data_surveillance_section_2',
        'content': section2_content
    })

# Debugging: Print the length and content of the data list
print(f"Number of sections extracted: {len(data)}")
print("Data extracted:")
for section in data:
    print(section)

# Convert data to JSON format
data_json = json.dumps(data, ensure_ascii=False)

# AWS S3 Configuration
s3_bucket_name = 'beacon-database'
s3_key = 'cdc_autism_data.json'

# Initialize Boto3 S3 client
s3_client = boto3.client('s3')
s3_client.delete_object(Bucket=s3_bucket_name, Key=s3_key)

# Upload data to S3
try:
    s3_client.put_object(Bucket=s3_bucket_name, Key=s3_key, Body=data_json)
    print("Data successfully uploaded to S3")
except Exception as e:
    print(f"Error uploading data to S3: {e}")

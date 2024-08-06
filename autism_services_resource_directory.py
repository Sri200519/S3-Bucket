import requests
import pdfplumber
import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Step 1: Download the PDF
url = "https://portal.ct.gov/-/media/dph/cyshcn/ct-collaborative-autism-services-resource-directory.pdf"
response = requests.get(url)
with open("resource_directory.pdf", "wb") as file:
    file.write(response.content)

# Step 2: Extract Data
def extract_text_from_pdf(pdf_path):
    text_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_data.extend(page.extract_text().split('\n'))
    return text_data

pdf_text_lines = extract_text_from_pdf("resource_directory.pdf")

# Step 3: Parse Data
def parse_text(lines):
    parsed_data = []
    entry = {}
    for line in lines:
        if line.strip() == '':  # Assuming a blank line indicates a new entry
            if entry:
                parsed_data.append(entry)
                entry = {}
        else:
            if "Organization:" in line:
                if entry:  # Save the previous entry if it exists
                    parsed_data.append(entry)
                entry = {"organization": line.replace("Organization:", "").strip()}
            elif "Contact:" in line:
                entry["contact_info"] = line.replace("Contact:", "").strip()
            elif "Services:" in line:
                entry["services"] = line.replace("Services:", "").strip()
            else:
                # Handle additional lines or append to existing entry fields
                if "additional_info" in entry:
                    entry["additional_info"] += " " + line.strip()
                else:
                    entry["additional_info"] = line.strip()
    if entry:
        parsed_data.append(entry)
    return parsed_data

structured_data = parse_text(pdf_text_lines)

# Convert structured data to JSON
json_data = json.dumps(structured_data, ensure_ascii=False, indent=4)

# Save JSON data to a file with UTF-8 encoding
with open('autism_services_resource_directory.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)

# AWS S3 configuration
s3_bucket_name = 'beacon-database'
s3_file_name = 'autism_services_resource_directory.json'

# Initialize the S3 client
s3 = boto3.client('s3', region_name='us-east-1')
s3.delete_object(Bucket=s3_bucket_name, Key=s3_file_name)

try:
    # Upload JSON file to S3
    s3.upload_file('autism_services_resource_directory.json', s3_bucket_name, s3_file_name)
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

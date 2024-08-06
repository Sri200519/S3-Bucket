from googleapiclient.discovery import build
import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from datetime import datetime

# Configuration
API_KEY = '***'  # Replace with your Google API Key
CALENDAR_ID = 'ctfoodbank.events@gmail.com'  # Replace with your public calendar ID

# Create the Google Calendar service object
service = build('calendar', 'v3', developerKey=API_KEY)

# Fetch events from the public calendar
now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=now,
                                       singleEvents=True, orderBy='startTime').execute()
events = events_result.get('items', [])

# Prepare data for JSON
data = []

for event in events:
    # Extract event details
    event_data = {
        'id': event.get('id'),
        'summary': event.get('summary', ''),
        'start': event.get('start', {}).get('dateTime', event.get('start', {}).get('date', '')),
        'end': event.get('end', {}).get('dateTime', event.get('end', {}).get('date', '')),
        'description': event.get('description', ''),
        'location': event.get('location', ''),
        'creator': event.get('creator', {}).get('email', '')
    }
    data.append(event_data)

# Convert data to JSON format
json_data = json.dumps(data, ensure_ascii=False, indent=4)

# Save JSON data to a file with UTF-8 encoding
with open('calendar_events.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)

# AWS S3 configuration
s3_bucket_name = 'beacon-database'
s3_file_name = 'calendar_events.json'

# Initialize the S3 client
s3 = boto3.client('s3', region_name='us-east-1')
s3.delete_object(Bucket=s3_bucket_name, Key=s3_file_name)

try:
    # Upload JSON file to S3
    s3.upload_file('calendar_events.json', s3_bucket_name, s3_file_name)
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

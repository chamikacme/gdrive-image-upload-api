import os
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from datetime import datetime
from googleapiclient.http import MediaIoBaseUpload
import base64
import io

load_dotenv()
FOLDER_ID = os.getenv('IMAGES_FOLDER_ID')
SHEET_ID = os.getenv('SHEET_ID')
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']

def get_credentials():
    credentials_dict = {
        "type": os.getenv('TYPE'),
        "project_id": os.getenv('PROJECT_ID'),
        "private_key_id": os.getenv('PRIVATE_KEY_ID'),
        "private_key": os.getenv('PRIVATE_KEY'),
        "client_email": os.getenv('CLIENT_EMAIL'),
        "client_id": os.getenv('CLIENT_ID'),
        "auth_uri": os.getenv('AUTH_URI'),
        "token_uri": os.getenv('TOKEN_URI'),
        "auth_provider_x509_cert_url": os.getenv('AUTH_PROVIDER_X509_CERT_URL'),
        "client_x509_cert_url": os.getenv('CLIENT_X509_CERT_URL'),
    }
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, SCOPES)
    return credentials

def write_to_sheet(id, filename,sheets_service):
    values = [[ datetime.now().strftime("%Y/%m/%d %H:%M:%S"), id, filename]]
    body = { 'values': values }
    try:
        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range='images!A2:C2',
            valueInputOption='RAW',
            body=body
        ).execute()

        print(f"Sheet updated successfully. Rows added: {result.get('updates').get('updatedRows')}")
    except Exception as error:
        print(f"An error occurred: {error}")
        raise

def upload(base64_data, filename, folder_id=FOLDER_ID):
    timpstampString = str(datetime.now().timestamp()).split(".")[0]
    filename = f"{timpstampString}-{filename}"
    file_data = base64.b64decode(base64_data)
    file_obj = io.BytesIO(file_data)
    file_obj.name = filename

    http = get_credentials().authorize(Http())
    drive_service = build('drive', 'v3', http=http)
    sheets_service = build('sheets', 'v4', http=http)

    file_metadata = {'name': file_obj.name}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    media_body = MediaIoBaseUpload(file_obj, mimetype='application/octet-stream')
    try:
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media_body,
            fields='id',
        ).execute()
        print(f"File uploaded successfully. ID: {file.get('id')}")
        write_to_sheet(file.get('id'), filename,sheets_service)
        return file
    except Exception as error:
        print(f"An error occurred: {error}")
        raise

def clear():
    http = get_credentials().authorize(Http())
    drive_service = build('drive', 'v3', http=http)
    sheets_service = build('sheets', 'v4', http=http)
    try:
        files = drive_service.files().list(q=f"'{FOLDER_ID}' in parents").execute().get('files', [])
        for file in files:
            drive_service.files().delete(fileId=file.get('id')).execute()
            print(f"File {file.get('name')} deleted successfully.")
        print(f"Folder {FOLDER_ID} cleared successfully.")
    except Exception as error:
        print(f"An error occurred: {error}")
        raise

    try:
        result = sheets_service.spreadsheets().values().clear(
            spreadsheetId=SHEET_ID,
            range='images!A2:C',
        ).execute()
        print(f"Sheet cleared successfully. Rows cleared: {result.get('clearedRange')}")
        return
    except Exception as error:
        print(f"An error occurred: {error}")
        raise
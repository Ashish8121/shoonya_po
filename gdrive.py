from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
from io import BytesIO

# ➡️ Define SCOPES (access only your files)
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_gdrive():
    """
    Authenticates using OAuth InstalledAppFlow.
    Opens a browser window to login the first time and saves token.pickle.
    Returns authenticated Google Drive service.
    """
    creds = None

    # ➡️ Load saved credentials if available
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # ➡️ If no valid creds, login using InstalledAppFlow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # 🔴 This opens your browser for Google OAuth consent screen
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # ➡️ Save credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # ➡️ Build and return service
    service = build('drive', 'v3', credentials=creds)
    return service


def create_or_get_folder(service, folder_name, parent_id=None):
    """
    Creates or retrieves a folder with folder_name.
    If parent_id is provided, searches/creates under that parent.
    Returns folder_id.
    """
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
    items = results.get('files', [])

    if items:
        return items[0]['id']
    else:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]

        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')


def upload_pdf_to_vendor_folder(pdf_bytes, vendor_name, purchase_orders_root_id):
    """
    Uploads PDF bytes to Google Drive:
    - Uses provided purchase_orders_root_id as 'Purchase Orders' folder
    - Creates vendor folder inside 'Purchase Orders'
    - Uploads PDF with today's date as filename in vendor folder
    Returns uploaded file ID.
    """
    service = authenticate_gdrive()

    # ➡️ Step 1: Get or create vendor folder inside 'Purchase Orders'
    vendor_folder_id = create_or_get_folder(service, vendor_name, parent_id=purchase_orders_root_id)

    # ➡️ Step 2: Upload file with today's date as name inside vendor folder
    today_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{today_date}.pdf"

    media = MediaIoBaseUpload(BytesIO(pdf_bytes), mimetype='application/pdf')
    file_metadata = {'name': filename, 'parents': [vendor_folder_id]}
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    print(f"✅ Uploaded {filename} to folder '{vendor_name}' inside 'Purchase Orders'. File ID: {file.get('id')}")
    return file.get('id')

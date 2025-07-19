# =========================
# po_id.py
# =========================

from datetime import datetime
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from io import BytesIO

def read_last_po_id(service, folder_id):
    """
    Reads last_po_id.txt content from Google Drive.
    Returns content string and file_id.
    """
    query = f"'{folder_id}' in parents and name='last_po_id.txt' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
    items = results.get('files', [])

    if items:
        file_id = items[0]['id']
        request = service.files().get_media(fileId=file_id)
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        fh.seek(0)
        content = fh.read().decode('utf-8').strip()
        return content, file_id
    else:
        # Initialize if not exists
        file_metadata = {
            'name': 'last_po_id.txt',
            'parents': [folder_id],
            'mimeType': 'text/plain'
        }
        initial_value = "0"
        media = MediaIoBaseUpload(BytesIO(initial_value.encode()), mimetype='text/plain')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return initial_value, file['id']

def update_last_po_id(service, file_id, new_value):
    """
    Updates last_po_id.txt in Drive with new_value.
    """
    media = MediaIoBaseUpload(BytesIO(new_value.encode()), mimetype='text/plain')
    service.files().update(fileId=file_id, media_body=media).execute()

def generate_po_id(service, folder_id):
    """
    Generates new PO ID with current year, reads and updates Drive.
    Format: YEAR-COUNT (e.g. 2025-000)
    """
    last_id_str, file_id = read_last_po_id(service, folder_id)
    last_id = int(last_id_str)
    new_id = last_id  # do not increment here for current ID

    year = datetime.now().year
    po_id = f"{year}-{new_id:03d}"

    # Update Drive file for next time with incremented value
    update_last_po_id(service, file_id, str(new_id + 1))
    return po_id


from googleapiclient.discovery import build
from google.oauth2 import service_account
import json

from common.config import SERVICE_ACCOUNT_FILE, SCRAPED_LINKS_PATH, read_json_data

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive = build('drive', 'v3', credentials=creds)

def list_folder(folder_id, depth=0, max_depth=3):
    """Recursively list all files/subfolders."""
    results = []
    page_token = None

    while True:
        resp = drive.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id, name, mimeType, webViewLink, size)",
            pageToken=page_token
        ).execute()

        for item in resp.get('files', []):
            item['depth'] = depth
            item['parent_id'] = folder_id
            results.append(item)

            # Recurse into subfolders
            if item['mimeType'] == 'application/vnd.google-apps.folder' and depth < max_depth:
                children = list_folder(item['id'], depth + 1, max_depth)
                results.extend(children)

        page_token = resp.get('nextPageToken')
        if not page_token:
            break

    return results

# Load the scraped folder list
folders = read_json_data(SCRAPED_LINKS_PATH)['pages']

all_files = []
seen_folder_ids = set()  # avoid re-crawling duplicate folder IDs

for entry in folders:
    fid = entry['folder_id']
    if not fid or fid in seen_folder_ids:
        continue
    seen_folder_ids.add(fid)
    print(f"Exploring: {entry['year']} | {entry.get('branch') or entry.get('subject')} ...")
    files = list_folder(fid)
    for f in files:
        f['source_context'] = entry  # attach metadata from website
    all_files.extend(files)

data = {
    "files": all_files,
}
write_json_file(SCRAPED_FILES_PATH, data)

print(f"Total files found: {len(all_files)}")

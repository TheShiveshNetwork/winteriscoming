from googleapiclient.discovery import build
from google.oauth2 import service_account

from common.config import (
    SERVICE_ACCOUNT_FILE,
    SCRAPED_LINKS_PATH,
    SCRAPED_FILES_PATH,
    read_json_data,
    write_json_file,
)

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

CHUNK_SIZE = 100

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive = build('drive', 'v3', credentials=creds)


# Streaming generator (no full list in memory)
def list_folder_stream(folder_id, depth=0, max_depth=3):
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
            yield item

            if (
                item['mimeType'] == 'application/vnd.google-apps.folder'
                and depth < max_depth
            ):
                yield from list_folder_stream(item['id'], depth + 1, max_depth)

        page_token = resp.get('nextPageToken')
        if not page_token:
            break

def process_all():
    config_data = read_json_data(SCRAPED_LINKS_PATH)
    folders = config_data["pages"]

    seen_folder_ids = set()

    all_files = []   # grows gradually (final dataset)
    buffer = []      # chunk buffer
    total_count = 0

    for entry in folders:
        fid = entry.get("folder_id")

        if not fid or fid in seen_folder_ids:
            continue

        seen_folder_ids.add(fid)

        print(
            f"Exploring: {entry.get('year')} | "
            f"{entry.get('branch') or entry.get('subject')} ..."
        )

        for f in list_folder_stream(fid):
            f["source_context"] = entry
            buffer.append(f)
            total_count += 1

            # Chunk flush
            if len(buffer) >= CHUNK_SIZE:
                all_files.extend(buffer)
                buffer.clear()

                write_json_file(
                    SCRAPED_FILES_PATH,
                    {"files": all_files}
                )

                print(f"Saved {len(all_files)} total files so far...")

    if buffer:
        all_files.extend(buffer)
        buffer.clear()

    write_json_file(
        SCRAPED_FILES_PATH,
        {"files": all_files}
    )

    print(f"\nTotal files found: {total_count}")


if __name__ == "__main__":
    process_all()

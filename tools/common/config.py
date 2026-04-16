import os, json, tempfile
from urllib.parse import urlparse

CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../config/site.json")
)
SCRAPED_LINKS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../data/scraped_links.json")
)
SCRAPED_FILES_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../data/files_links.json")
)

SERVICE_ACCOUNT_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../secrets/google_service_account.json")
)

class ConfigError(Exception):
    pass

def read_json_data(path: str) -> dict:
    """Safely read the json data from a file"""
    if not os.path.exists(path):
        raise ConfigError(f"Config file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config: {e}") from e
    except OSError as e:
        raise ConfigError(f"File read error: {e}") from e

    if not isinstance(data, dict):
        raise ConfigError(f"Expected JSON object in {path}, got {type(data).__name__}")

    return data

def write_json_file(path: str, data: dict):
    dir_path = os.path.dirname(path)

    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    try:
        json.dumps(data)
    except (TypeError, OverflowError) as e:
        raise ValueError(f"Data is not JSON serializable: {e}") from e

    try:
        with tempfile.NamedTemporaryFile("w", delete=False, dir=dir_path, encoding="utf-8") as tmp:
            json.dump(data, tmp, indent=2)
            temp_name = tmp.name
        os.replace(temp_name, path)

    except OSError as e:
        raise RuntimeError(f"Failed to write file {path}: {e}") from e


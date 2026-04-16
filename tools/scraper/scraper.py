import requests
from bs4 import BeautifulSoup
import json
import re
import os

from common.config import CONFIG_PATH, SCRAPED_LINKS_PATH, read_json_data, write_json_file

def get_config_field_value(field_name: str, expected_type: Type | None = None) -> Any:
    """Get the value of the field from the config"""
    data = read_json_data(CONFIG_PATH)

    if field_name not in data:
        raise ConfigError(f"Missing field '{field_name}' in {CONFIG_PATH}")

    value = data[field_name]

    if expected_type and not isinstance(value, expected_type):
        raise ConfigError(
            f"Field '{field_name}' must be of type {expected_type.__name__}, "
            f"got {type(value).__name__}"
        )

    return value

def extract_folder_id(url):
    """Extract the Drive folder ID from a Google Drive URL."""
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None

def scrape_first_year(soup):
    """First year has Stream > Cycle > Subject structure."""
    results = []
    current_stream = None
    current_cycle = None

    for tag in soup.find_all(['h2', 'h3', 'li']):
        if tag.name == 'h2':
            current_stream = tag.get_text(strip=True)
        elif tag.name == 'h3':
            current_cycle = tag.get_text(strip=True)
        elif tag.name == 'li':
            link = tag.find('a', href=re.compile(r'drive\.google\.com'))
            if link:
                subject = link.get_text(strip=True).replace(' ▾', '')
                url = link['href']
                results.append({
                    "year": "First Year",
                    "stream": current_stream,
                    "cycle": current_cycle,
                    "branch": None,
                    "subject": subject,
                    "drive_url": url,
                    "folder_id": extract_folder_id(url),
                })
    return results

def scrape_year_by_branch(soup, year_label):
    """2nd/3rd/4th year: Branch > Drive folder URL."""
    results = []
    # Each branch is a section with h3 + a[href*=drive]
    sections = soup.find_all('h3')
    for section in sections:
        branch = section.get_text(strip=True)
        # The View link is usually in the next sibling <a> or nearby <p>/<div>
        next_el = section.find_next('a', href=re.compile(r'drive\.google\.com'))
        if next_el:
            url = next_el['href']
            results.append({
                "year": year_label,
                "stream": None,
                "cycle": None,
                "branch": branch,
                "subject": None,
                "drive_url": url,
                "folder_id": extract_folder_id(url),
            })
    return results

def scrape_all():
    all_links = []
    site_pages = get_config_field_value("pages", dict)
    for year_key, url in site_pages.items():
        print(f"Scraping {url}...")
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

        if year_key == "first":
            links = scrape_first_year(soup)
        else:
            year_label = year_key.capitalize() + " Year"
            links = scrape_year_by_branch(soup, year_label)

        all_links.extend(links)
        print(f"\tFound {len(links)} Drive folder links")

    return all_links

if __name__ == "__main__":
    data = {
        "pages": scrape_all(),
    }
    write_json_file(SCRAPED_LINKS_PATH, data)

    print(f"\nTotal: {len(data['pages'])} Drive folder links saved to {SCRAPED_LINKS_PATH}")


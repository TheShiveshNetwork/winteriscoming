# Semestr Tools

These tools are helper utilities designed to support the data ingestion pipeline. They facilitate web scraping, Google Drive exploration, and data analysis.

## Setup

This project uses `uv` for dependency management. Ensure you have it installed before proceeding.

1. **Install Dependencies:**
   ```bash
   uv sync
   ```

2. **Configuration:**
   Ensure your configuration files and service account keys are in place as required by the `common/config.py`.

## Tools

### 1. Scraper
Scrapes links and metadata from configured web sources.
```bash
uv run scraper/scraper.py
```

### 2. GDrive Explorer
Explores and retrieves metadata/files from Google Drive using service account credentials.
```bash
uv run gdrive/explorer.py
```

### 3. Analyzer
Processes and visualizes the collected data using DataFrames and terminal-based plotting.
```bash
uv run analyzer/analyzer.py
```

## Note
These tools are intended to be used as modular helpers within the broader ingestion workflow, rather than standalone applications.

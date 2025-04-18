# 📝 Quotes Scraper to Google Sheets

This project is a Python-based web scraper that extracts quotes from [quotes.toscrape.com](http://quotes.toscrape.com) and writes them into a Google Sheets spreadsheet using the Google Sheets API.

It uses:

- `requests` and `BeautifulSoup` for web scraping
- `gspread` and `google-auth` for interacting with Google Sheets
- A virtual environment to manage dependencies

---

## 🚀 Features

- Scrapes quote text, author, and tags from the main page
- Sends data to a pre-configured Google Sheet
- Clears and replaces existing data
- Includes error handling and request timeouts
- Ready for future features like pagination, scheduling, and login-protected scraping

---

## 🔧 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/LolRB/Data-Parsing.git
cd Data-Parsing
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux
```

### 3. Install dependencies

```bash
pip install requests beautifulsoup4 gspread google-auth
```

If you don’t have a requirements.txt yet, install manually:
```bash
pip install -r requirements.txt
```

## 📄 Google Sheets API Setup

1. Go to Google Cloud Console

2. Create a new project and enable:

    - Google Sheets API

    - Google Drive API

3. Create a Service Account, generate a JSON key, and download it.

4. Save the file as credentials.json in the project root.

5. Share your target Google Sheet with the service account email (found in the JSON file).

## ✏️ Configuration

In scrape_to_sheets.py:

```python
SPREADSHEET_NAME = 'Your Google Sheet Name'
SHEET_NAME = 'Your Sheet Name'
```
Make sure these names match your actual spreadsheet and tab.

## ▶️ Running the Script

From your activated environment:

```bash
python scrape_to_sheets.py
```
If successful, the quotes will appear in your Google Sheet with columns:

- Quote

- Author

- Tags

## 🛡️ Error Handling

- Includes a timeout to prevent hanging requests

- Logs network and request errors

- Gracefully handles missing spreadsheet/tab names

## 📌 To Do / Roadmap
 - ✅ Basic scraping from open website

 - ✅ Writing to Google Sheets

 - ✅ Virtual environment + config

 - 🟩 Pagination support

 - 🟩 Scheduled auto-execution (e.g., every 12h)

 - 🟩 Login-protected scraping

 - 🟩 Data formatting & visual enhancements in Sheets

## 🧑‍💻 Author

Created by Rodrigo Bueno

Feel free to fork, extend, or contribute!
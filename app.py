"""This script scrapes quotes from a website and saves them to Google Sheets."""

import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials

# Configuración: URLs y credenciales
LOGIN_URL = "https://prodep.capacitacioncontinua.mx/login/index.php"
DATA_URL = "https://prodep.capacitacioncontinua.mx/local/kopere_dashboard/view.php?classname=reports&method=load_report&type=course&report=3&courseid=12"
USERNAME = "manager"       # <-- Reemplazar con el nombre de usuario correcto
PASSWORD = "m4N4G3R*"    # <-- Reemplazar con la contraseña correcta

# Google Sheets config

# Archivo JSON de la cuenta de servicio
SERVICE_ACCOUNT_FILE = 'credentials.json'
# Puede ser el nombre del documento de Google Sheets
SPREADSHEET_NAME = 'Prueba Data Parsing'
SHEET_NAME = 'Hoja 1'  # Nombre de la pestaña/hoja dentro del documento


# Clases de encabezados que queremos extraer (y el orden deseado de columnas)
TARGET_HEADER_CLASSES = [
    "th_userid",
    "th_userfullname",
    "th_email",
    "th_timecreated",
    "th_activities_completed",
    "th_activities_assigned",
    "th_course_completed"
]

# ---------------------------------------

# Google Sheets authorization
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)

# Step 1: Request the quotes page
URL = 'http://quotes.toscrape.com/'

try:
    response = requests.get(URL, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
except requests.exceptions.Timeout:
    print("⏰ Request timed out.")
    soup = None
except requests.exceptions.RequestException as e:
    print(f"🚨 Request failed: {e}")
    soup = None

if soup:
    # continue parsing
    quotes = soup.select('.quote')

# Step 2: Parse quotes
quotes = soup.select('.quote')  # select all quote blocks

data = [['Quote', 'Author', 'Tags']]  # header row

for quote in quotes:
    text = quote.select_one('.text').get_text(strip=True)
    author = quote.select_one('.author').get_text(strip=True)
    tags = [tag.get_text(strip=True) for tag in quote.select('.tags .tag')]
    tags_str = ', '.join(tags)
    data.append([text, author, tags_str])

# Step 3: Write to Google Sheets
sheet.clear()  # clear existing content (optional)
sheet.update('A1', data)  # write all data starting from A1

print("✅ Quotes scraped and saved to Google Sheets.")

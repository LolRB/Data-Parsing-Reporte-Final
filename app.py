"""Este script obtiene calificaciones de Moodle y las exporta a Google Sheets."""

import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials

# Configuración – estos valores deberían estar definidos apropiadamente
USERNAME = "manager"        # <- reemplazar por el usuario de Moodle
PASSWORD = "m4N4G3R*"    # <- reemplazar por la contraseña de Moodle
COURSE_ID = 12
SPREADSHEET_NAME = "Prueba Data Parsing"
WORKSHEET_NAME = "Hoja 1"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

session = requests.Session()

# 1. Obtener la página de login para extraer el logintoken
LOGIN_URL = "https://prodep.capacitacioncontinua.mx/login/index.php"
res = session.get(LOGIN_URL, headers=HEADERS, verify=False)
res.raise_for_status()
match = re.search(r'name="logintoken" value="(\w+)"', res.text)
if not match:
    raise ValueError("No se encontró logintoken en la página de login")
logintoken = match.group(1)

# 2. Enviar formulario de login
login_data = {
    "username": USERNAME,
    "password": PASSWORD,
    "anchor": "",
    "logintoken": logintoken
}
res = session.post(LOGIN_URL, data=login_data,
                   allow_redirects=False, headers=HEADERS, verify=False)
res.raise_for_status()

if 300 <= res.status_code < 400:
    next_url = res.headers.get("Location")
    if next_url:
        res = session.get(next_url, headers=HEADERS, verify=False)
        res.raise_for_status()

dashboard_html = res.text
sesskey_match = re.search(
    r'sesskey["\']*:?\s*["\']([a-zA-Z0-9]+)', dashboard_html)
if not sesskey_match:
    raise ValueError("No se encontró sesskey tras login.")
sesskey = sesskey_match.group(1)

# 3. Obtener usuarios del curso
ajax_url_base = "https://prodep.capacitacioncontinua.mx/lib/ajax/service.php"
payload_users = [{
    "index": 0,
    "methodname": "gradereport_grader_get_users_in_report",
    "args": {"courseid": COURSE_ID}
}]
url_users = f"{ajax_url_base}?sesskey={sesskey}&info=gradereport_grader_get_users_in_report"
resp1 = session.post(url_users, json=payload_users,
                     headers=HEADERS, verify=False)
resp1.raise_for_status()
users_result = resp1.json()

user_list = []
user_info = {}
if users_result and isinstance(users_result, list):
    data_part = users_result[0].get("data", {})
    users = data_part.get("users", data_part)
    for u in users:
        uid = u.get("id")
        fullname = u.get("fullname")
        email = u.get("email")
        if uid is not None:
            user_list.append(uid)
            user_info[uid] = {"name": fullname, "email": email}

# 4. Obtener calificaciones por usuario
# CAMBIO: Extraer calificaciones directamente del HTML de la tabla de calificaciones
grades_url = f"https://prodep.capacitacioncontinua.mx/grade/report/grader/index.php?id={COURSE_ID}"
res_grades_html = session.get(grades_url, headers=HEADERS, verify=False)
res_grades_html.raise_for_status()

soup_grades = BeautifulSoup(res_grades_html.text, "html.parser")

# CAMBIO: Acotar búsqueda a la tabla específica de calificaciones
grades_table = soup_grades.find("table", {"id": "user-grades"})
if not grades_table:
    raise ValueError(
        "No se encontró la tabla de calificaciones con id='user-grades'.")

# Definir los items que deseamos extraer
target_item_ids = {74: "Entregable 3",
                   110: "Entregable 2", 236: "Entregable 1"}

grades_by_user = {}  # Inicializar estructura por usuario

# CAMBIO: Mapear por itemid y buscar en el HTML por ID u[USERID]i[ITEMID]
for uid in user_list:
    grades_by_user[uid] = {}
    for item_id, nombre_item in target_item_ids.items():
        celda_id = f"u{uid}i{item_id}"
        # CAMBIO: depuración opcional
        print(f"🔍 Buscando celda con id: {celda_id}")
        celda = grades_table.find("td", {"id": celda_id})
        valor = ""
        if celda:
            span = celda.find("span", class_="gradevalue")
            if span:
                valor = span.get_text(strip=True)
        grades_by_user[uid][item_id] = valor

# 5. Preparar datos para Google Sheets
headers = ["Nombre completo", "Email",
           "Entregable 1", "Entregable 2", "Entregable 3"]
table_data = [headers]
for uid in user_list:
    info = user_info.get(uid)
    if not info:
        continue
    row = [
        info.get("name", ""),
        info.get("email", ""),
        grades_by_user.get(uid, {}).get(236, ""),
        grades_by_user.get(uid, {}).get(110, ""),
        grades_by_user.get(uid, {}).get(74, "")
    ]
    table_data.append(row)

# 6. Enviar a Google Sheets
creds = Credentials.from_service_account_file("credentials.json", scopes=[
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
])

try:
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)

    # Verificar que hay datos para subir (mínimo encabezados + 1 fila)
    if len(table_data) <= 1:
        raise ValueError(
            "No se generaron filas válidas para actualizar la hoja de cálculo.")

    # Limpiar contenido anterior
    sheet.clear()

    # 🕒 Agregar timestamp en la celda A1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.update("A1", [[f"Actualizado el: {timestamp}"]])

    # 📊 Preparar los datos para iniciar en la celda B1
    sheet.update("B1", table_data)

    # Registrar timestamp en hoja de historial
    try:
        log_sheet = client.open(SPREADSHEET_NAME).worksheet("Historial")
    except gspread.exceptions.WorksheetNotFound:
        log_sheet = client.open(SPREADSHEET_NAME).add_worksheet(
            title="Historial", rows="100", cols="2")

    log_sheet.append_row(
        ["Ejecución registrada el:", timestamp])  # Cada fila nueva

    print("✅ Datos actualizados correctamente en la hoja de Google Sheets.")

except ValueError as e:
    print(f"❌ Error al actualizar Google Sheets: {e}")

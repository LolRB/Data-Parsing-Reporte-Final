"""This script scrapes quotes from a website and saves them to Google Sheets."""

import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuración: URLs y credenciales
LOGIN_URL = "https://prodep.capacitacioncontinua.mx/login/index.php"
DATA_URL = "https://prodep.capacitacioncontinua.mx/local/kopere_dashboard/view-ajax.php?classname=reports&method=getdata&report=3&courseid=12"

USERNAME = "manager"
PASSWORD = "m4N4G3R*"

# Google Sheets config
SERVICE_ACCOUNT_FILE = 'credentials.json'
SPREADSHEET_NAME = 'Prueba Data Parsing'
WORKSHEET_NAME = 'Hoja 1'

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

try:
    # 1. Iniciar sesión en el sitio web
    session = requests.Session()
    resp_login_page = session.get(LOGIN_URL, headers=HEADERS, verify=False)
    resp_login_page.raise_for_status()

    # Obtener token del formulario
    soup_login = BeautifulSoup(resp_login_page.text, "html.parser")
    token_input = soup_login.find("input", {"name": "logintoken"})
    login_token = token_input["value"] if token_input else ""
    print("DEBUG token:", login_token)

    # Preparar y enviar login
    login_data = {
        "username": USERNAME,
        "password": PASSWORD,
        "anchor": "",
    }
    if login_token:
        login_data["logintoken"] = login_token

    resp_login = session.post(
        LOGIN_URL, data=login_data, headers=HEADERS, verify=False)

    if "username" in resp_login.text.lower() and "password" in resp_login.text.lower():
        raise ValueError(
            "Inicio de sesión FALLIDO: Verifique el usuario y la contraseña.")
    print("✅ Sesión iniciada correctamente.")

    # 2. Preparar payload de la solicitud POST al endpoint JSON
    payload = {
        "draw": 1,
        "start": 0,
        "length": 1000
    }

    for i, campo in enumerate([
        "userid", "userfullname", "email", "timecreated",
        "activities_completed", "activities_assigned", "course_completed"
    ]):
        payload[f"columns[{i}][data]"] = campo
        payload[f"columns[{i}][name]"] = ""
        payload[f"columns[{i}][searchable]"] = "true"
        payload[f"columns[{i}][orderable]"] = "false"
        payload[f"columns[{i}][search][value]"] = ""
        payload[f"columns[{i}][search][regex]"] = "false"

    resp_data = session.post(DATA_URL, headers=HEADERS,
                             data=payload, verify=False)
    resp_data.raise_for_status()

    # # 3. Extraer los datos de la tabla en la página protegida
    # soup_data = BeautifulSoup(resp_data.text, "html.parser")
    # table = soup_data.find("table")
    # if table is None:
    #     raise Exception(
    #         "No se encontró la tabla de datos en la página protegida.")
    # print("DEBUG tabla HTML:\n", table.prettify()[:1000])  # Muestra los primeros 1000 caracteres

    # # Identificar las columnas de interés por clase en el encabezado
    # header_cells = table.find_all("th")
    # if not header_cells:
    #     raise Exception(
    #         "La tabla no tiene encabezados <th>, estructura inesperada.")
    # # Crear un diccionario para mapear la clase de encabezado a su índice de columna
    # col_index = {}
    # for idx, th in enumerate(header_cells):
    #     if not th.get("class"):
    #         continue
    #     # Una celda th puede tener múltiples clases, verificamos cada una
    #     for cls in th.get("class"):
    #         if cls in TARGET_HEADER_CLASSES:
    #             col_index[cls] = idx
    # # Verificar que se encontraron todas las columnas necesarias
    # for cls in TARGET_HEADER_CLASSES:
    #     if cls not in col_index:
    #         raise Exception(f"No se encontró la columna esperada: {cls}")

    # # Extraer encabezados de la tabla (texto)
    # header_values = []
    # for cls in TARGET_HEADER_CLASSES:
    #     idx = col_index[cls]
    #     # Obtener el texto del encabezado en ese índice
    #     header_text = header_cells[idx].get_text(strip=True)
    #     header_values.append(header_text)

    # # Recorrer las filas del cuerpo de la tabla y extraer columnas deseadas
    # data_rows = []
    # tbody = table.find("tbody")
    # if not tbody:
    #     # Si no hay <tbody>, tomar todas las filas después del encabezado
    #     table_rows = table.find_all("tr")[1:]
    # else:
    #     table_rows = tbody.find_all("tr")
    # for row in table_rows:
    #     # algunas tablas podrían usar <th> para celdas de cuerpo
    #     cells = row.find_all(["td", "th"])
    #     if not cells:
    #         continue  # saltar si la fila está vacía o no tiene celdas
    #     # Extraer valores en el orden de TARGET_HEADER_CLASSES
    #     row_data = []
    #     for cls in TARGET_HEADER_CLASSES:
    #         idx = col_index.get(cls)
    #         if idx is not None and idx < len(cells):
    #             cell_text = cells[idx].get_text(strip=True)
    #         else:
    #             cell_text = ""
    #         row_data.append(cell_text)
    #     data_rows.append(row_data)

    # # Verificar que se obtuvieron filas de datos
    # if not data_rows:
    #     raise Exception(
    #         "La tabla está vacía o no se pudieron extraer filas de datos.")

    # 3. Extraer datos del JSON
    try:
        json_data = resp_data.json()
        print("DEBUG JSON keys:", json_data.keys())
        print("DEBUG JSON preview:", str(json_data)[:500])
    except Exception as exc:
        raise ValueError(
            "No se pudo interpretar la respuesta como JSON. Verifica si la sesión sigue activa.") from exc

    registros = json_data.get("data", [])

    if not registros:
        raise ValueError("No se encontraron datos en el JSON.")

    # Campos a extraer
    campos = ["userid", "userfullname", "email", "timecreated",
              "activities_completed", "activities_assigned", "course_completed"]

    header_values = campos
    data_rows = []

    for reg in registros:
        fila = [reg.get(campo, "") for campo in campos]
        data_rows.append(fila)

    # 4. Conectar con Google Sheets
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scope)
    client = gspread.authorize(creds)

    try:
        spreadsheet = client.open(SPREADSHEET_NAME)
    except Exception as exc:
        raise ValueError(
            f"No se pudo abrir la hoja de cálculo: {exc}") from exc

    try:
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
    except Exception as exc:
        raise ValueError(
            f"No se encontró la pestaña '{WORKSHEET_NAME}' en la hoja de cálculo: {exc}") from exc

    # 5. Actualizar hoja
    worksheet.clear()
    all_data = [header_values] + data_rows
    worksheet.update("A1", all_data)

    print("✅ Datos actualizados correctamente en la hoja de Google Sheets.")

except ValueError as err:
    print(f"ERROR: {err}")

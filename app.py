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

try:
    # 1. Iniciar sesión en el sitio web
    session = requests.Session()
    resp_login_page = session.get(LOGIN_URL)
    resp_login_page.raise_for_status()  # Verifica que se obtuvo respuesta 200 OK

    # Parsear el HTML de la página de login para obtener el token oculto
    soup_login = BeautifulSoup(resp_login_page.text, "html.parser")
    token_input = soup_login.find("input", {"name": "logintoken"})
    login_token = token_input["value"] if token_input else ""

    # Preparar los datos de inicio de sesión (usuario, contraseña, token y anchor vacío)
    login_data = {
        "username": USERNAME,
        "password": PASSWORD,
        "anchor": "",
    }
    if login_token:
        login_data["logintoken"] = login_token

    # Enviar la solicitud POST de login con las credenciales
    resp_login = session.post(LOGIN_URL, data=login_data)
    # Comprobar si el login fue exitoso buscando alguna evidencia de sesión iniciada.
    # Por ejemplo, si la respuesta sigue mostrando el formulario de login, significa que falló.
    if "login" in resp_login.url or "error" in resp_login.text.lower():
        raise Exception(
            "Inicio de sesión FALLIDO: Verifique el usuario y la contraseña.")

    # 2. Navegar a la página protegida (reporte) una vez iniciada la sesión
    resp_data = session.get(DATA_URL)
    resp_data.raise_for_status()

    # 3. Extraer los datos de la tabla en la página protegida
    soup_data = BeautifulSoup(resp_data.text, "html.parser")
    table = soup_data.find("table")
    if table is None:
        raise Exception(
            "No se encontró la tabla de datos en la página protegida.")

    # Identificar las columnas de interés por clase en el encabezado
    header_cells = table.find_all("th")
    if not header_cells:
        raise Exception(
            "La tabla no tiene encabezados <th>, estructura inesperada.")
    # Crear un diccionario para mapear la clase de encabezado a su índice de columna
    col_index = {}
    for idx, th in enumerate(header_cells):
        if not th.get("class"):
            continue
        # Una celda th puede tener múltiples clases, verificamos cada una
        for cls in th.get("class"):
            if cls in TARGET_HEADER_CLASSES:
                col_index[cls] = idx
    # Verificar que se encontraron todas las columnas necesarias
    for cls in TARGET_HEADER_CLASSES:
        if cls not in col_index:
            raise Exception(f"No se encontró la columna esperada: {cls}")

    # Extraer encabezados de la tabla (texto)
    header_values = []
    for cls in TARGET_HEADER_CLASSES:
        idx = col_index[cls]
        # Obtener el texto del encabezado en ese índice
        header_text = header_cells[idx].get_text(strip=True)
        header_values.append(header_text)

    # Recorrer las filas del cuerpo de la tabla y extraer columnas deseadas
    data_rows = []
    tbody = table.find("tbody")
    if not tbody:
        # Si no hay <tbody>, tomar todas las filas después del encabezado
        table_rows = table.find_all("tr")[1:]
    else:
        table_rows = tbody.find_all("tr")
    for row in table_rows:
        # algunas tablas podrían usar <th> para celdas de cuerpo
        cells = row.find_all(["td", "th"])
        if not cells:
            continue  # saltar si la fila está vacía o no tiene celdas
        # Extraer valores en el orden de TARGET_HEADER_CLASSES
        row_data = []
        for cls in TARGET_HEADER_CLASSES:
            idx = col_index.get(cls)
            if idx is not None and idx < len(cells):
                cell_text = cells[idx].get_text(strip=True)
            else:
                cell_text = ""
            row_data.append(cell_text)
        data_rows.append(row_data)

    # Verificar que se obtuvieron filas de datos
    if not data_rows:
        raise Exception(
            "La tabla está vacía o no se pudieron extraer filas de datos.")

    # 4. Conectar a Google Sheets usando la cuenta de servicio
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scope)
    client = gspread.authorize(creds)
    # Abrir la hoja de cálculo (por nombre del documento y luego nombre de hoja)
    try:
        spreadsheet = client.open(SPREADSHEET_NAME)
    except Exception as e:
        raise Exception(f"No se pudo abrir la hoja de cálculo: {e}")
    try:
        worksheet = spreadsheet.worksheet(SHEET_NAME)
    except Exception as e:
        raise Exception(
            f"No se encontró la pestaña '{SHEET_NAME}' en la hoja de cálculo: {e}")

    # 5. Reemplazar completamente los datos existentes en la hoja con los nuevos datos
    worksheet.clear()  # Limpia todo el contenido actual de la hoja
    # Preparar los datos a subir: incluir encabezados en la primera fila, seguido de las filas de datos
    all_data = [header_values] + data_rows
    # Actualizar la hoja de cálculo empezando desde la celda A1 con el nuevo contenido
    worksheet.update("A1", all_data)

    print("Datos actualizados correctamente en la hoja de Google Sheets.")

except Exception as err:
    # 6. Manejo de errores: imprimir el mensaje de error y finalizar
    print(f"ERROR: {err}")

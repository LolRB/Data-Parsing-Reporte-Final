# 📊 Automatización de Exportación de Calificaciones a Google Sheets

Este proyecto permite automatizar la extracción de calificaciones de un curso en Moodle y exportarlas a una hoja de cálculo en Google Sheets. Está diseñado específicamente para plataformas Moodle como `https://prodep.capacitacioncontinua.mx`.

## 🚀 Características

- Inicia sesión de forma automática en la plataforma Moodle de Prodep.
- Recupera nombres, correos electrónicos y calificaciones de entregables específicos.
- Formatea los datos en una tabla con nombre completo, correo electrónico y calificaciones.
- Limpia y actualiza los datos en la hoja de Google Sheets definida.
- Registra un timestamp en cada ejecución (en una hoja separada).
- Permite programar su ejecución periódica (por ejemplo, con el Programador de tareas o cron).

## 📂 Estructura del proyecto

```
├── app.py              # Script principal 
├── credentials.json    # Clave de servicio de Google 
├── README.md           # Documentación del proyecto
```

## 🔧 Requisitos

- Python 3.8 o superior
- Cuenta de servicio de Google Cloud y archivo credentials.json con permisos de Sheets y Drive
- Acceso al curso en Moodle con credenciales válidas

## 🔧 Instalación

### 1. Clona el repositorio privado

Para clonar este repositorio, asegúrate de tener acceso autorizado en GitHub.

- SSH (recomendado) si tienes configurada tu clave SSH:

```bash
git clone git@github.com:LolRB/Data-Parsing-Reporte-Final.git
cd Data-Parsing-Reporte-Final
```

- HTTPS (te pedirá usuario y contraseña o token personal):

```bash
git clone https://github.com/LolRB/Data-Parsing-Reporte-Final.git
cd Data-Parsing-Reporte-Final
```

🔒 Nota: Si usas HTTPS, GitHub puede solicitar un token de acceso personal en lugar de tu contraseña.

### 2. Crea y activa un entorno virtual (opcional pero recomendado):

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux
```

### 3. Instala las dependencias:

```bash
pip install requests beautifulsoup4 gspread google-auth
```

## 📄 Google Sheets API Setup

1. Ve a Google Cloud Console

2. Crea un nuevo proyecto y habilita:

    - Google Sheets API

    - Google Drive API

3. Cree una cuenta de servicio, genere una clave JSON y descárguela.

4. Guarde el archivo como credentials.json en la raíz del proyecto.

5. Comparta su hoja de cálculo de Google de destino con el correo electrónico de la cuenta de servicio (que se encuentra en el archivo JSON).

## ✏️ Configuración

En app.py, define las siguientes variables al inicio del archivo:

```python
USERNAME = "usuario"        # Usuario de Moodle
PASSWORD = "password"       # Contraseña de Moodle
COURSE_ID = 33               # ID del curso en Moodle
SPREADSHEET_NAME = "Prueba"  # Nombre de la hoja de cálculo en Google Sheets
WORKSHEET_NAME = "Hoja 1"               # Nombre de la pestaña dentro de la hoja
```
Asegúrese de que estos nombres coincidan con su hoja de cálculo y pestaña reales.

## ▶️ Ejecuta el Script

Ejecuta el siguiente comando para obtener y subir las calificaciones:

```bash
python app.py
```
Al finalizar, en la celda A1 aparecerá el sello de tiempo de la última actualización y en B1 comenzará la tabla con los datos.

Cada ejecución:

- Vacía el contenido anterior de la hoja.

- Crea una tabla con nombre completo, correo electrónico y calificaciones.

- Registra un timestamp en otra hoja llamada Historial.

## 🕒 Automatización (opcional)

Puedes usar:

- 🪟 Windows: Programador de tareas ejecutando un archivo .bat.

- 🐧 Linux/macOS: Cron job ejecutando un .sh.

## 🛠 Tecnologías utilizadas

- Python

- Requests

- BeautifulSoup

- gspread

- Google API Python Client

## 📌 Notas

- Este script fue probado en plataformas Moodle personalizadas, por lo que podrían requerirse ajustes si cambia la estructura HTML.

- El verify=False está activo para ignorar advertencias de certificados SSL. Se recomienda desactivarlo si cuentas con certificados válidos.

## 🧑‍💻 Author

Para dudas o sugerencias, contáctame por email: [ztmsiul79@gmail.com](mailto:ztmsiul79@gmail.com).

Creado por Rodrigo Bueno.
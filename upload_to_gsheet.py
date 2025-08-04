import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# --- Configuration ---
# Path to your service account JSON file
SERVICE_ACCOUNT_FILE = "D:/My_Work/M.Salah Task/Streamlit/sharqawi-reports-0e89fb6c3b24.json"

# URL of your Google Sheets file
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1DFk4HC8DSTwJyyb7RNcihd72-6G1HN19WmIpxauGWv8/edit#gid=0"

# Path to your Excel file
EXCEL_FILE = "D:/My_Work/M.Salah Task/Streamlit/Search_Report.xlsx"

# --- Load Excel Data ---
# Read the first sheet from the Excel file
df = pd.read_excel(EXCEL_FILE, sheet_name=0)
df = df.fillna("")  # Replace NaN with empty string


# --- Authenticate with Google Sheets ---
# Define the required access scopes
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from the JSON file
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scope)

# Authorize the client
client = gspread.authorize(credentials)

# --- Update Google Sheet ---
# Open the target sheet by its URL
sheet = client.open_by_url(SPREADSHEET_URL)

# Select the first worksheet
worksheet = sheet.get_worksheet(0)

# Clear existing content
worksheet.clear()

# Upload new data (headers + values)
worksheet.update([df.columns.values.tolist()] + df.values.tolist())

print("✅ Data uploaded successfully to Google Sheets.")

# Step 1: Import libraries
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Step 2: Load the Excel file
excel_path = r"D:\My_Work\M.Salah Task\Streamlit\Search_Report.xlsx"
df = pd.read_excel(excel_path, sheet_name=0)

# Step 3: Authenticate with Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
secrets_path = r"D:\My_Work\M.Salah Task\Streamlit\sharqawi-reports-0e89fb6c3b24.json"
creds = Credentials.from_service_account_file(secrets_path, scopes=scopes)
client = gspread.authorize(creds)

# Step 4: Open the target Google Sheet
sheet_url = "https://docs.google.com/spreadsheets/d/1DFk4HC8DSTwJyyb7RNcihd72-6G1HN19WmIpxauGWv8/edit?usp=sharing"
sheet = client.open_by_url(sheet_url)
worksheet = sheet.get_worksheet(0)  # First sheet

# Step 5: Clear old data
worksheet.clear()

# Step 6: Upload DataFrame to Google Sheet
worksheet.update([df.columns.values.tolist()] + df.values.tolist())

print("✅ Upload to Google Sheets completed successfully.")

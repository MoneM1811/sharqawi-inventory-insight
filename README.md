# 🔍 Sharqawi Inventory Insight

**Live inventory tracking, vendor balances, and smart search in one place.**

This Streamlit app helps monitor live inventory with advanced filtering and beautifully formatted reports. It includes:

- ✅ Live sync with Google Sheets (auto-update using Python).
- ✅ Smart filtering by material, description, vendor number, and vendor name.
- ✅ Colored indicators for negative balances and zero quantity.
- ✅ Beautiful signature footer for professionalism.
- ✅ Export options for Excel or CSV.

---

## 📊 Data Source

The data is pulled directly from a Google Sheets file:
[Inventory Sheet](https://docs.google.com/spreadsheets/d/1DFk4HC8DSTwJyyb7RNcihd72-6G1HN19WmIpxauGWv8)

---

## 🛠️ Technologies Used

- Python + Streamlit
- Pandas
- Google Sheets API (`gspread`)
- Google Cloud Service Account
- VS Code + GitHub

---

## 🔁 Auto-Sync Local Excel to Google Sheet

To automatically upload the latest local `Search_Report.xlsx` to Google Sheets, use this function in your Python export code:

```python
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

def upload_to_gsheet_from_local(path):
    df = pd.read_excel(path)
    creds = Credentials.from_service_account_file("your_service_account.json")  # Replace with your actual file path
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1DFk4HC8DSTwJyyb7RNcihd72-6G1HN19WmIpxauGWv8")
    worksheet = sheet.get_worksheet(0)
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# Example usage:
upload_to_gsheet_from_local("D:/My_Work/M.Salah Task/Streamlit/Search_Report.xlsx")

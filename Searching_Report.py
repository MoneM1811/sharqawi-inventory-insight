import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from PIL import Image
import os

# Auto-update Google Sheet with latest data
import gspread
from google.oauth2.service_account import Credentials

def upload_to_gsheet(df, sheet_url):
    # Drop rows/columns with invalid values
    df = df.fillna("")  # Replace NaN with empty strings

    # Load credentials from secrets
    creds_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(creds_dict)
    client = gspread.authorize(credentials)

    # Open the Google Sheet
    sheet = client.open_by_url(sheet_url)
    worksheet = sheet.get_worksheet(0)

    # Clear existing content then update
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# Call the function after generating search_df
upload_to_gsheet(search_df, "https://docs.google.com/spreadsheets/d/1DFk4HC8DSTwJyyb7RNcihd72-6G1HN19WmIpxauGWv8")

# --- إعداد الصفحة ---
st.set_page_config(page_title="Sharqawi Inventory Search", layout="wide")

st.markdown("## 📦 Sharqawi Inventory Search Report")
st.markdown("Use the filters below to explore the inventory status by material or vendor.")

# --- بيانات الاعتماد الخاصة بـ Google Sheets ---
@st.cache_resource
def connect_to_gsheet():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )
    client = gspread.authorize(credentials)
    return client

# --- تحميل البيانات من Google Sheets ---
@st.cache_data(ttl=3600)  # تحديث كل ساعة
def load_data():
    client = connect_to_gsheet()
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1DFk4HC8DSTwJyyb7RNcihd72-6G1HN19WmIpxauGWv8/edit?usp=sharing")
    worksheet = sheet.sheet1
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    # تنسيق الأعمدة
    df['Last_issue'] = pd.to_datetime(df['Last_issue'], errors='coerce').dt.strftime('%Y-%m-%d')
    df['Last_Received'] = pd.to_datetime(df['Last_Received'], errors='coerce').dt.strftime('%Y-%m-%d')
    df['Vendor_Balance'] = df['Vendor_Balance'].apply(lambda x: f"{x:,.1f}")
    df['Store_Qunt'] = df['Store_Qunt'].apply(lambda x: f"{x:,.2f}")
    df['last_RCV_Cost'] = df['last_RCV_Cost'].apply(lambda x: f"{x:,.3f}")

    return df

search_df = load_data()

# --- Sidebar Filters ---
material = st.sidebar.text_input("🔍 Search by Material")
description = st.sidebar.text_input("📝 Material Description")
vendor_no = st.sidebar.text_input("🏷️ Vendor No.")
vendor_name = st.sidebar.text_input("👤 Vendor Name")

filtered_df = search_df.copy()

if material:
    filtered_df = filtered_df[filtered_df['Material'].astype(str).str.contains(material, case=False)]

if description:
    filtered_df = filtered_df[filtered_df['Material Description'].astype(str).str.contains(description, case=False)]

if vendor_no:
    filtered_df = filtered_df[filtered_df['Vendor No.'].astype(str).str.contains(vendor_no, case=False)]

if vendor_name:
    filtered_df = filtered_df[filtered_df['Vendor Name'].astype(str).str.contains(vendor_name, case=False)]

# --- Highlighting Logic ---
def highlight_background(val, col):
    try:
        numeric_val = float(val.replace(',', ''))
    except:
        return ''

    if col == "Store_Qunt":
        if numeric_val == 0:
            return 'background-color: #ffeaea'  # very light red
        elif numeric_val < 0:
            return 'background-color: #ffcccc'  # light red
        else:
            return 'background-color: #e6ffea'  # light green
    elif col == "Vendor_Balance":
        if numeric_val < 0:
            return 'background-color: #ffe6e6'
    return ''

# Apply styles
styled_df = filtered_df.style \
    .applymap(lambda val: highlight_background(val, 'Store_Qunt'), subset=['Store_Qunt']) \
    .applymap(lambda val: highlight_background(val, 'Vendor_Balance'), subset=['Vendor_Balance'])

# --- Display Table ---
st.markdown("### 📊 Filtered Inventory Data")
st.dataframe(styled_df, use_container_width=True)

# --- Export Section ---
st.markdown("### 📁 Export Data")
col1, col2 = st.columns(2)

with col1:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download CSV", data=csv, file_name="Sharqawi_Inventory.csv", mime="text/csv")

with col2:
    excel_export_path = r"D:\\My_Work\\M.Salah Task\\Streamlit\\Sharqawi_Inventory_Export.xlsx"
    filtered_df.to_excel(excel_export_path, index=False)
    st.success(f"Excel exported to: {excel_export_path}")

# --- Footer Section ---
st.markdown("---")
st.markdown("### 👤 Contact")
col3, col4 = st.columns([1, 6])

with col3:
    st.image("https://i.ibb.co/f8pbpHn/profile.jpg", width=80)  # You can upload your photo to a URL like imgbb.com

with col4:
    st.markdown("**Abdelmonem A. Rashed**  ")
    st.markdown("📧 monem1811@gmail.com")
    st.markdown("📍 Sharqawi Air Distribution Factory")

# --- Footer Signature ---
from PIL import Image

st.markdown("---")
col1, col2 = st.columns([1, 5])
with col1:
    st.image("my_photo.png", width=60)  # Adjust size if needed
with col2:
    st.markdown("""
    **Abdelmonem A. Rashed**  
    Financial Cost Control & Data Analyst  
    📧 [ARashed@SharqawiFactory.com](mailto:ARashed@SharqawiFactory.com)  
    🔗 [LinkedIn](https://www.linkedin.com/in/MonemRashed)
    """)

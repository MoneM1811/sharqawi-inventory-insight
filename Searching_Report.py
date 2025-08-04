import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from PIL import Image
from google.oauth2.service_account import Credentials

# --- Page Configuration ---
st.set_page_config(page_title="Sharqawi Inventory Insight", layout="wide")

# --- Title & Description ---
st.title("🔍 Sharqawi Inventory Insight")
st.caption("*Live inventory tracking, vendor balances, and smart search in one place.*")

# --- Auto-upload to Google Sheets ---
@st.cache_resource
def upload_to_gsheet(df, sheet_url):
    df = df.fillna("")
    creds_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(creds_dict)
    client = gspread.authorize(credentials)
    worksheet = client.open_by_url(sheet_url).get_worksheet(0)
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# --- Upload latest search_df automatically (if exists) ---
if 'search_df' in locals():
    upload_to_gsheet(search_df, "https://docs.google.com/spreadsheets/d/1DFk4HC8DSTwJyyb7RNcihd72-6G1HN19WmIpxauGWv8")

# --- Google Sheet Connection ---
@st.cache_resource
def connect_to_gsheet():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    return gspread.authorize(credentials)

# --- Load Data from Sheet ---
@st.cache_data(ttl=3600)
def load_data():
    sheet = connect_to_gsheet().open_by_url(
        "https://docs.google.com/spreadsheets/d/1DFk4HC8DSTwJyyb7RNcihd72-6G1HN19WmIpxauGWv8/edit?usp=sharing"
    ).sheet1
    df = pd.DataFrame(sheet.get_all_records())

    # Format date columns safely
    if 'Last_issue' in df.columns:
        df['Last_issue'] = pd.to_datetime(df['Last_issue'], errors='coerce').dt.strftime('%Y-%m-%d')
    if 'Last_Received' in df.columns:
        df['Last_Received'] = pd.to_datetime(df['Last_Received'], errors='coerce').dt.strftime('%Y-%m-%d')

    # Format numeric columns with checks
    if 'Vendor_Balance' in df.columns:
        df['Vendor_Balance'] = pd.to_numeric(df['Vendor_Balance'], errors='coerce').apply(
            lambda x: f"{x:,.1f}" if pd.notnull(x) else "")
    if 'Store_Qunt' in df.columns:
        df['Store_Qunt'] = pd.to_numeric(df['Store_Qunt'], errors='coerce').apply(
            lambda x: f"{x:,.2f}" if pd.notnull(x) else "")
    if 'last_RCV_Cost' in df.columns:
        df['last_RCV_Cost'] = pd.to_numeric(df['last_RCV_Cost'], errors='coerce').apply(
            lambda x: f"{x:,.3f}" if pd.notnull(x) else "")

    if 'Store_unit' in df.columns:
        df['Store_unit'] = df['Store_unit'].fillna("")

    return df

search_df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("🔎 Filters")
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

# --- Conditional Formatting ---
def highlight_background(val, col):
    try:
        numeric_val = float(val.replace(',', ''))
    except:
        return ''
    if col == "Store_Qunt":
        if numeric_val == 0:
            return 'background-color: #ffeaea'
        elif numeric_val < 0:
            return 'background-color: #ffcccc'
        else:
            return 'background-color: #e6ffea'
    elif col == "Vendor_Balance" and numeric_val < 0:
        return 'background-color: #ffe6e6'
    return ''

styled_df = filtered_df.style \
    .applymap(lambda val: highlight_background(val, 'Store_Qunt'), subset=['Store_Qunt']) \
    .applymap(lambda val: highlight_background(val, 'Vendor_Balance'), subset=['Vendor_Balance'])

# --- Display Table ---
st.markdown("### 📊 Filtered Inventory Data")
st.dataframe(styled_df, use_container_width=True, height=700)

# --- Export Options ---
st.markdown("### 📁 Export Options")
col1, col2 = st.columns(2)

with col1:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download CSV", data=csv, file_name="Sharqawi_Inventory.csv", mime="text/csv")

# --- Footer Signature ---
st.markdown("---")
footer_col1, footer_col2 = st.columns([1, 6])
with footer_col1:
    st.image("my_photo.png", width=50)
with footer_col2:
    st.markdown("""
    **Abdelmonem A. Rashed**  
    Financial Cost Control & Data Analyst  
    📧 [ARashed@SharqawiFactory.com](mailto:ARashed@SharqawiFactory.com)  
    🔗 [LinkedIn](https://www.linkedin.com/in/MonemRashed)
    """)

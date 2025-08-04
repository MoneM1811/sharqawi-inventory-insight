# FINAL VERSION of Streamlit Inventory App for Streamlit Cloud
# With correct formatting of Store_Qunt, Vendor_Balance, and last_RCV_Cost

import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from PIL import Image
from google.oauth2.service_account import Credentials

# --- Page Configuration ---
st.set_page_config(page_title="Sharqawi Inventory Insight", layout="wide")

# --- Title & Description ---
st.title("\U0001F50D Sharqawi Inventory Insight")
st.caption("*Live inventory tracking, vendor balances, and smart search in one place.*")
if st.button("\U0001F504 Reload Latest Data"):
    st.cache_data.clear()
    st.experimental_rerun()

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
    return clean_dataframe(df)

# --- Clean and Format Data ---
def clean_dataframe(df):
    if 'Material' in df.columns:
        df['Material'] = df['Material'].astype(str)

    if 'Store_unit' in df.columns:
        df['Store_unit'] = df['Store_unit'].astype(str).fillna("").replace("nan", "")

    if 'Vendor_Balance' in df.columns:
        df['Vendor_Balance'] = pd.to_numeric(df['Vendor_Balance'], errors='coerce')
        df['Vendor_Balance'] = df['Vendor_Balance'].apply(lambda x: f"{x:,.1f}" if pd.notnull(x) else "")

    if 'Store_Qunt' in df.columns:
        df['Store_Qunt'] = pd.to_numeric(df['Store_Qunt'], errors='coerce')
        df['Store_Qunt'] = df['Store_Qunt'].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "")

    if 'last_RCV_Cost' in df.columns:
        df['last_RCV_Cost'] = pd.to_numeric(df['last_RCV_Cost'], errors='coerce')
        df['last_RCV_Cost'] = df['last_RCV_Cost'].apply(lambda x: f"{x:,.3f}" if pd.notnull(x) else "")

    return df

# --- Load and Upload Data ---
search_df = load_data()
upload_to_gsheet(search_df, "https://docs.google.com/spreadsheets/d/1DFk4HC8DSTwJyyb7RNcihd72-6G1HN19WmIpxauGWv8")

# --- Sidebar Filters ---
st.sidebar.header("\U0001F50E Filters")
material = st.sidebar.text_input("\U0001F50D Search by Material")
description = st.sidebar.text_input("\U0001F4DD Material Description")
vendor_no = st.sidebar.text_input("\U0001F3F7️ Vendor No.")
vendor_name = st.sidebar.text_input("\U0001F464 Vendor Name")

filtered_df = search_df.copy()
if material:
    filtered_df = filtered_df[filtered_df['Material'].str.contains(material, case=False)]
if description:
    filtered_df = filtered_df[filtered_df['Material Description'].str.contains(description, case=False)]
if vendor_no:
    filtered_df = filtered_df[filtered_df['Vendor No.'].astype(str).str.contains(vendor_no, case=False)]
if vendor_name:
    filtered_df = filtered_df[filtered_df['Vendor Name'].str.contains(vendor_name, case=False)]

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
    .map(lambda val: highlight_background(val, 'Store_Qunt'), subset=['Store_Qunt']) \
    .map(lambda val: highlight_background(val, 'Vendor_Balance'), subset=['Vendor_Balance'])

# --- Display Table ---
st.markdown("### \U0001F4CA Filtered Inventory Data")
st.dataframe(styled_df, use_container_width=True, height=700)

# --- Export Options ---
st.markdown("### \U0001F4C1 Export Options")
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

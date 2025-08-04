# Reporting_System_3.py

import streamlit as st
from PIL import Image
from modules import production, sales, purchase, accounting, hr, store
from config import THEMES  # New config file

# --- Page Config ---
st.set_page_config(page_title="📊 Sharqawi Reporting", layout="wide")

# --- Load Logo ---
logo = Image.open("sharqawi_logo.png")
col1, col2 = st.columns([1, 6])
with col1:
    st.image(logo, width=140)
with col2:
    st.markdown("<h1 style='margin-top: 15px; color: #1f77b4;'>Sharqawi Air Distribution Factory</h1>", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; margin-top: 0;'>📊 Integrated Reporting System</h2>", unsafe_allow_html=True)
st.markdown("---")

# --- Main Menu ---
main_menu = st.sidebar.selectbox("📁 Select Section", list(THEMES.keys()))

# --- Submenus ---
submenus = {
    "Sales": ["Sales Summary", "Aging Report", "Collection Report"],
    "Production": ["Production Summary"],
    "Purchase": ["Vendor Summary", "Purchase Budget"],
    "Store": ["Inventory", "Stock Movement"],
    "Accounting": ["Costing", "Cash Flow", "Income Statement"],
    "Human Resources": ["Headcount", "Attendance", "Payroll"]
}
submenu = st.sidebar.radio("🧭 Choose a report", submenus.get(main_menu, []))

# --- Theming ---
theme = THEMES.get(main_menu, {"color": "#1f77b4", "icon": "📊"})
st.markdown(
    f"<style>h3.section-title {{ color: {theme['color']}; }}</style>", 
    unsafe_allow_html=True
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 Created by")
st.sidebar.markdown("**Abdelmonem A. Rashed**  \n[ARashed@SharqawiFactory.com](mailto:ARashed@SharqawiFactory.com)")

# --- Route to Module ---
if main_menu == "Sales":
    if submenu == "Sales Summary":
        sales.render_sales_reports()
    elif submenu == "Aging Report":
        st.info("🕐 Aging Report coming soon...")
    elif submenu == "Collection Report":
        st.info("📥 Collection Report coming soon...")

elif main_menu == "Production":
    production.render_production_report()

elif main_menu == "Purchase":
    st.info("📦 Purchase reports under construction...")

elif main_menu == "Store":
    st.info("🏪 Store reports under construction...")

elif main_menu == "Accounting":
    st.info("📊 Accounting reports under construction...")

elif main_menu == "Human Resources":
    st.info("👥 HR reports under construction...")

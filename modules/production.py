# At the top of modules/production.py
def render_production_report():
    st.write("✅ Production Report Loaded")

# modules/production.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from config import THEMES

# File paths
PRODUCTION_FILE_PATH = r"\\192.168.1.2\Producation_Summary\Mng Production_Summary ShApp.xlsx"
INVOICE_FILE_PATH = r"\\192.168.1.2\InvoiceAmount\Mng Invoice_InvoiceAmount R01.xlsx"

# --- Main Function ---
def render_production_report():
    theme = THEMES["Production"]
    section_color = theme["color"]

    # --- Title Styling ---
    st.markdown(f"<h3 class='section-title'>🏗️ Production Report Section</h3>", unsafe_allow_html=True)
    st.markdown(f"""
        <style>
        .section-title {{
            font-size: 26px;
            font-weight: 700;
            color: {section_color};
            text-align: center;
        }}
        .sub-section-title {{
            font-size: 20px;
            font-weight: 600;
            color: {section_color};
            background-color: #e3f2fd;
            padding: 10px;
            border-radius: 6px;
            margin-top: 20px;
        }}
        </style>
    """, unsafe_allow_html=True)

    # --- Subsection: Load Data ---
    st.markdown("<div class='sub-section-title'>📦 Production Summary</div>", unsafe_allow_html=True)

    try:
        df = pd.read_excel(PRODUCTION_FILE_PATH)
        keep_columns = ["Customer", "Project", "JobOrder", "Weight[KG]", "PRDComplete", "JobOrder_Phase", "JobOrder_Dep", "JobOrder_Status"]
        df_filtered = df[[col for col in keep_columns if col in df.columns]].copy()
    except Exception as e:
        st.error(f"❌ Error loading production file: {e}")
        return

    try:
        df_invoice = pd.read_excel(INVOICE_FILE_PATH)
        df_invoice.dropna(how='all', inplace=True)
        df_invoice.columns = df_invoice.columns.str.strip()
        df_invoice = df_invoice[["Job Order", "Prf.Invoice [SAR]"]].copy()
        df_invoice.rename(columns={"Job Order": "JobOrder", "Prf.Invoice [SAR]": "Prf.Invoice"}, inplace=True)
    except Exception as e:
        st.error(f"❌ Error loading invoice file: {e}")
        return

    # --- Merge and Clean ---
    df_merged = pd.merge(df_filtered, df_invoice, on="JobOrder", how="left")
    df_merged["PRDComplete"] = pd.to_datetime(df_merged["PRDComplete"], errors='coerce')
    df = df_merged.dropna(subset=["PRDComplete"])

    # --- Time Periods ---
    today = datetime.today()
    this_year = today.year
    last_year = this_year - 1
    this_month = today.month

    df_ytd = df[df["PRDComplete"].dt.year == this_year]
    df_ly_ytd = df[df["PRDComplete"].dt.year == last_year]
    df_mtd = df[(df["PRDComplete"].dt.year == this_year) & (df["PRDComplete"].dt.month == this_month)]

    # --- Summary Table ---
    def summary(df_period, label):
            return pd.DataFrame({
                "Report Period": [label],
                "Completed Weight (KG) ⚙️": [f"{df_period['Weight[KG]'].sum():,.0f}"],
                "Completed Orders 📦": [df_period["JobOrder"].nunique()]
            })
    st.markdown("<div class='sub-section-title'>📋 Production KPIs</div>", unsafe_allow_html=True)

    summary_df = pd.concat([
        summary(df_ytd, "📅 Year to Date"),
        summary(df_ly_ytd, "📅 Same Period Last Year"),
        summary(df_mtd, "📆 Month to Date")
    ])
    st.dataframe(summary_df, use_container_width=True)

    # --- Monthly Weight Chart ---
    st.markdown("<div class='sub-section-title'>🏗️ Production Overview</div>", unsafe_allow_html=True)


    df_plot = df[df["PRDComplete"].dt.year.isin([this_year, last_year])].copy()
    df_plot["Month"] = df_plot["PRDComplete"].dt.to_period("M").astype(str)
    df_plot["Year"] = df_plot["PRDComplete"].dt.year

    monthly = df_plot.groupby(["Month", "Year"])["Weight[KG]"].sum().reset_index()
    monthly.rename(columns={"Weight[KG]": "Total Weight"}, inplace=True)
    monthly["Month"] = pd.to_datetime(monthly["Month"])
    monthly = monthly.sort_values("Month")
    monthly["Month"] = monthly["Month"].dt.strftime("%b %Y")

    fig = px.line(
        monthly,
        x="Month", y="Total Weight", color="Year",
        markers=True,
        title="📈 Monthly Production Weight: Last Year vs Current Year",
        labels={"Total Weight": "Weight (KG)", "Month": "Month"}
    )
    fig.update_layout(legend_title_text="Year")
    st.plotly_chart(fig, use_container_width=True)

    # --- Top Customers by Weight ---
    st.markdown("<div class='sub-section-title'>🏅 Top 10 Customers & Projects This Month</div>", unsafe_allow_html=True)

    top_customers = df_mtd.groupby(["Customer", "Project"])["Weight[KG]"].sum().reset_index()
    top_customers = top_customers.sort_values("Weight[KG]", ascending=False).head(10)
    st.dataframe(top_customers, use_container_width=True)

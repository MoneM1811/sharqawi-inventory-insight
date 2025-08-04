# At the top of modules/production.py
def render_sales_report():
    st.write("✅ sales Report Loaded")

# modules/sales.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from config import THEMES

# File paths
SALES_PATH_2024 = r"D:\My_Work\M.Salah Task\SAP\Sales all time\2024.XLSX"
SALES_PATH_2025 = r"D:\My_Work\M.Salah Task\SAP\Sales all time\2025.XLSX"
PROD_SUMMARY_PATH = r"\\192.168.1.2\Producation_Summary\Mng Production_Summary ShApp.xlsx"

# --- Main Report Function ---
def render_sales_reports():
    theme = THEMES["Sales"]  # 🎨 Use green theme
    section_color = theme["color"]

    # --- Page Title ---
    st.markdown(f"<h3 class='section-title'>💵 Sales Report Section</h3>", unsafe_allow_html=True)
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
            background-color: #e8f5e9;
            padding: 10px;
            border-radius: 6px;
            margin-top: 20px;
        }}
        </style>
    """, unsafe_allow_html=True)

    # --- Subsection: Load and Prepare Data ---
    st.markdown("<div class='sub-section-title'>🧾 Sales Summary</div>", unsafe_allow_html=True)

    try:
        df_2024 = pd.read_excel(SALES_PATH_2024)
        df_2025 = pd.read_excel(SALES_PATH_2025)
        df_prod = pd.read_excel(PROD_SUMMARY_PATH)
    except Exception as e:
        st.error(f"❌ Error loading files: {e}")
        return

    # 💡 Standardize column names
    rename_cols = {
        "Sold-to party": "CustomerID",
        "Name 1": "Customer Name",
        "Billing Date": "Billing Date",
        "Down Payment": "Down Payment",
        "Net Value": "Net Value"
    }
    df_2024.rename(columns=rename_cols, inplace=True)
    df_2025.rename(columns=rename_cols, inplace=True)
    df_prod.rename(columns=lambda x: x.strip(), inplace=True)

    # 💡 Convert dates and calculate total sales
    df_2024["Billing Date"] = pd.to_datetime(df_2024["Billing Date"], errors='coerce')
    df_2025["Billing Date"] = pd.to_datetime(df_2025["Billing Date"], errors='coerce')
    df_2024["Total Sales"] = df_2024["Down Payment"].fillna(0) + df_2024["Net Value"].fillna(0)
    df_2025["Total Sales"] = df_2025["Down Payment"].fillna(0) + df_2025["Net Value"].fillna(0)

    # 💡 Merge Sales Engineer info from production summary
    df_2024["CustomerID"] = df_2024["CustomerID"].astype(str)
    df_2025["CustomerID"] = df_2025["CustomerID"].astype(str)
    df_prod["CustomerID"] = df_prod["CustomerID"].astype(str)

    if 'PRDComplete' in df_prod.columns:
        df_prod["PRDComplete"] = pd.to_datetime(df_prod["PRDComplete"], errors='coerce')
        latest_saleseng = df_prod[df_prod["PRDComplete"].dt.year == 2025].sort_values("PRDComplete")
        latest_saleseng = latest_saleseng.drop_duplicates("CustomerID", keep="last")
        df_2024 = df_2024.merge(latest_saleseng[["CustomerID", "SalesEng"]], on="CustomerID", how="left")
        df_2025 = df_2025.merge(latest_saleseng[["CustomerID", "SalesEng"]], on="CustomerID", how="left")

    # --- Subsection: Summary Table ---
    today = datetime.today()
    start_2024 = datetime(2024, 1, 1)
    start_2025 = datetime(2025, 1, 1)

    ytd_2024 = df_2024[(df_2024["Billing Date"] >= start_2024) & (df_2024["Billing Date"] < start_2025)]
    ytd_2025 = df_2025[(df_2025["Billing Date"] >= start_2025) & (df_2025["Billing Date"] <= today)]
    mtd_2025 = df_2025[df_2025["Billing Date"].dt.month == today.month]
    lmd_2025 = df_2025[df_2025["Billing Date"].dt.month == (today.month - 1 if today.month > 1 else 12)]

    summary_table = pd.DataFrame({
        "Report": [
            "🗓️ YTD 2024", "🗓️ YTD 2025", "🗓️ MTD 2025", f"📅 Last Month ({lmd_2025['Billing Date'].dt.strftime('%B').iloc[0] if not lmd_2025.empty else '-'})"
        ],
        "Total Sales 💵": [
            f"{ytd_2024['Total Sales'].sum():,.0f}",
            f"{ytd_2025['Total Sales'].sum():,.0f}",
            f"{mtd_2025['Total Sales'].sum():,.0f}",
            f"{lmd_2025['Total Sales'].sum():,.0f}"
        ]
    })
    st.dataframe(summary_table, use_container_width=True)

    # --- Subsection: Monthly Comparison Table ---
    st.markdown("<div class='sub-section-title'>📊 Monthly Comparison Table</div>", unsafe_allow_html=True)

    df_chart = pd.concat([
        df_2024.assign(Year=2024),
        df_2025.assign(Year=2025)
    ])
    df_chart["Month"] = df_chart["Billing Date"].dt.month
    df_chart.dropna(subset=["Billing Date"], inplace=True)

    monthly_sales = df_chart.groupby(["Year", "Month"])["Total Sales"].sum().unstack(level=0).fillna(0)
    monthly_sales = monthly_sales.reindex(range(1, 13), fill_value=0)
    monthly_sales.index = pd.date_range("2024-01-01", periods=12, freq='M').strftime("%b")
    monthly_sales["% Change"] = ((monthly_sales[2025] - monthly_sales[2024]) / monthly_sales[2024].replace(0, 1)) * 100
    monthly_sales.loc["Total"] = [
        monthly_sales[2024].sum(),
        monthly_sales[2025].sum(),
        ((monthly_sales[2025].sum() - monthly_sales[2024].sum()) / monthly_sales[2024].sum()) * 100
    ]
    monthly_sales[2024] = monthly_sales[2024].map("{:,.0f}".format)
    monthly_sales[2025] = monthly_sales[2025].map("{:,.0f}".format)
    monthly_sales["% Change"] = monthly_sales["% Change"].map("{:.1f}%".format)
    st.dataframe(monthly_sales.rename(columns={2024: "2024", 2025: "2025", "% Change": "Variation %"}), use_container_width=True)

    # --- Subsection: Monthly Sales Chart ---
    st.markdown("<div class='sub-section-title'>📈 Monthly Sales Chart</div>", unsafe_allow_html=True)

    df_chart["Month Label"] = df_chart["Billing Date"].dt.strftime("%b")
    monthly = df_chart.groupby(["Month Label", "Year"])["Total Sales"].sum().reset_index()
    monthly = monthly.sort_values(by="Month Label", key=lambda x: pd.to_datetime(x, format='%b'))

    fig = px.line(monthly, x="Month Label", y="Total Sales", color="Year", markers=True,
                  title="📊 Monthly Sales Comparison 2024 vs 2025",
                  labels={"Total Sales": "Sales (SAR)", "Month Label": "Month"})
    st.plotly_chart(fig, use_container_width=True)

    # --- Subsection: Top 10 Customers ---
    st.markdown("<div class='sub-section-title'>🏆 Top 10 Customers</div>", unsafe_allow_html=True)

    top_customers = df_2025.groupby(["CustomerID", "Customer Name", "SalesEng"])["Total Sales"].sum().reset_index()
    top_customers = top_customers.sort_values("Total Sales", ascending=False).head(10)
    top_customers["Total Sales"] = top_customers["Total Sales"].map("{:,.0f}".format)
    st.dataframe(top_customers, use_container_width=True)

    # --- Subsection: Sales by SalesEng ---
    st.markdown("<div class='sub-section-title'>🌟 Sales by SalesEng</div>", unsafe_allow_html=True)

    sales_by_eng = df_2025.groupby("SalesEng")["Total Sales"].sum().reset_index()
    sales_by_eng = sales_by_eng.sort_values("Total Sales", ascending=False)
    sales_by_eng["Total Sales"] = sales_by_eng["Total Sales"].map("{:,.0f}".format)
    st.dataframe(sales_by_eng, use_container_width=True)

    fig_pie = px.pie(sales_by_eng, names="SalesEng", values="Total Sales",
                     title="💼 Sales Distribution by Sales Engineer")
    st.plotly_chart(fig_pie, use_container_width=True)

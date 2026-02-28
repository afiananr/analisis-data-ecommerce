import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os
from babel.numbers import format_currency

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="E-Commerce Comprehensive Dashboard", layout="wide")
sns.set_style("whitegrid")

# =========================
# LOAD DATA
# =========================
current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_dir, "main_data.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(data_path)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

main_df = load_data()

# =========================
# SIDEBAR FILTER
# =========================
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.header("Filter Transaksi")

    min_date = main_df["order_purchase_timestamp"].min()
    max_date = main_df["order_purchase_timestamp"].max()

    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

filtered_df = main_df[
    (main_df["order_purchase_timestamp"] >= pd.to_datetime(start_date)) &
    (main_df["order_purchase_timestamp"] <= pd.to_datetime(end_date))
]

# =========================
# HEADER
# =========================
st.title("E-Commerce Performance Dashboard 📊")
st.write(f"Analyst: **Afiana Nurani** | Periode: {start_date} s/d {end_date}")
st.markdown("---")

# =========================
# KPI METRICS
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    total_rev = filtered_df["price"].sum()
    st.metric("Total Revenue", format_currency(total_rev, 'BRL', locale='pt_BR'))

with col2:
    st.metric("Total Orders", f"{filtered_df['order_id'].nunique():,}")

with col3:
    st.metric("Unique Customers", f"{filtered_df['customer_unique_id'].nunique():,}")

st.markdown("---")

# =========================
# 1. BEST & WORST CATEGORY
# =========================
st.subheader("Pertanyaan 1: Best & Worst Performing Product Category")

category_revenue = (
    filtered_df.groupby("product_category_name_english")["price"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

col_left, col_right = st.columns(2)

with col_left:
    st.write("**Top 5 Categories (Best)**")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=category_revenue.head(5),
        x="price", y="product_category_name_english",
        ax=ax
    )
    ax.set_xlabel("Total Revenue (BRL)")
    ax.set_ylabel(None)
    st.pyplot(fig)

with col_right:
    st.write("**Bottom 5 Categories (Worst)**")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=category_revenue.sort_values("price").head(5),
        x="price", y="product_category_name_english",
        ax=ax
    )
    ax.set_xlabel("Total Revenue (BRL)")
    ax.set_ylabel(None)
    st.pyplot(fig)

st.markdown("---")

# =========================
# 2. CUSTOMER DISTRIBUTION BY STATE
# =========================
st.subheader("Pertanyaan 2: Customer Distribution by State")

state_dist = (
    filtered_df.groupby("customer_state")["customer_id"]
    .nunique()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=state_dist, x="customer_id", y="customer_state", ax=ax)

ax.set_xlabel("Number of Customers")
ax.set_ylabel("State")

for i, v in enumerate(state_dist["customer_id"]):
    ax.text(v, i, f" {v:,}", va="center")

st.pyplot(fig)

st.markdown("---")

# =========================
# 3. CUSTOMER LOYALTY SEGMENTATION
# =========================
st.subheader("Analisis Lanjutan: Customer Loyalty Segmentation")

loyalty_counts = filtered_df.groupby("customer_unique_id")["order_id"].nunique().reset_index()
loyalty_counts.columns = ['id', 'frequency']

loyalty_counts['segment'] = loyalty_counts['frequency'].apply(
    lambda x: "Loyalist" if x > 5 else ("Repeat Customer" if x >= 2 else "One-time Buyer")
)

loyalty_final = loyalty_counts['segment'].value_counts().reset_index()
loyalty_final.columns = ['Segment', 'Count']
total = loyalty_final["Count"].sum()

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(data=loyalty_final, x="Count", y="Segment", ax=ax)

for i, v in enumerate(loyalty_final["Count"]):
    ax.text(v, i, f" {v:,} ({v/total:.1%})", va="center")

st.pyplot(fig)

st.markdown("---")

# =========================
# 4. RFM DISTRIBUTION
# =========================
st.subheader("RFM Analysis: Customer Distribution")

now = filtered_df["order_purchase_timestamp"].max()
rfm_df = filtered_df.groupby("customer_unique_id").agg({
    "order_purchase_timestamp": lambda x: (now - x.max()).days,
    "order_id": "nunique",
    "price": "sum"
}).reset_index()

rfm_df.columns = ["customer_id", "recency", "frequency", "monetary"]

col_r, col_f, col_m = st.columns(3)

with col_r:
    st.write("**Recency Distribution (Days)**")
    fig, ax = plt.subplots()
    sns.histplot(rfm_df["recency"], bins=30, ax=ax)
    st.pyplot(fig)

with col_f:
    st.write("**Frequency Distribution**")
    fig, ax = plt.subplots()
    sns.histplot(rfm_df["frequency"], bins=20, ax=ax)
    st.pyplot(fig)

with col_m:
    st.write("**Monetary Distribution**")
    fig, ax = plt.subplots()
    sns.histplot(rfm_df["monetary"], bins=30, ax=ax)
    st.pyplot(fig)

st.markdown("---")

# =========================
# 5. REVENUE TREND
# =========================
st.subheader("Revenue Trend Over Time")

monthly_rev = (
    filtered_df
    .set_index("order_purchase_timestamp")
    .resample("M")["price"]
    .sum()
    .reset_index()
)

fig, ax = plt.subplots(figsize=(12, 5))
sns.lineplot(data=monthly_rev, x="order_purchase_timestamp", y="price", marker="o", ax=ax)
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (BRL)")
st.pyplot(fig)

# =========================
# FOOTER
# =========================
st.caption("© 2026 - Afiana Nurani | Information Systems UPN Veteran Jawa Timur")
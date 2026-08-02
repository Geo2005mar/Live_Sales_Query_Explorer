"""
Live Sales Query Explorer — Streamlit UI.

Runs filtered SELECT queries against the `orders` table that generator.py
keeps populating in the background, and auto-refreshes so newly inserted
rows show up without a manual reload.
"""

from datetime import datetime, timedelta

import mysql.connector
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from config import AMOUNT_MAX, AMOUNT_MIN, CATEGORIES, COUNTRIES, DB_CONFIG

st.set_page_config(page_title="Live Sales Query Explorer", page_icon="📈", layout="wide")


@st.cache_resource
def get_connection():
    conn = mysql.connector.connect(**DB_CONFIG)
    conn.autocommit = True
    return conn


def run_query(sql, params):
    conn = get_connection()
    if not conn.is_connected():
        conn.reconnect(attempts=3, delay=1)
    return pd.read_sql(sql, conn, params=params)


st.title("📈 Live Sales Query Explorer")
st.caption("MySQL + Streamlit — τα δεδομένα ενημερώνονται live από ένα background generator.")

with st.sidebar:
    st.header("Φίλτρα")

    default_start = datetime.now().date() - timedelta(days=60)
    default_end = datetime.now().date()
    date_range = st.date_input(
        "Εύρος ημερομηνιών",
        value=(default_start, default_end),
    )

    selected_categories = st.multiselect(
        "Κατηγορία προϊόντος",
        options=list(CATEGORIES.keys()),
    )

    selected_countries = st.multiselect(
        "Χώρα",
        options=COUNTRIES,
    )

    amount_range = st.slider(
        "Ποσό (€)",
        min_value=AMOUNT_MIN,
        max_value=AMOUNT_MAX,
        value=(AMOUNT_MIN, AMOUNT_MAX),
        step=5.0,
    )

    search_clicked = st.button("🔍 Αναζήτηση", type="primary", use_container_width=True)

    st.divider()
    auto_refresh = st.checkbox("Auto-refresh", value=True)
    refresh_seconds = st.slider("κάθε (δευτ.)", 3, 30, 5, disabled=not auto_refresh)

if auto_refresh:
    st_autorefresh(interval=refresh_seconds * 1000, key="live_refresh")

# Build the dynamic WHERE clause from the selected filters.
where_clauses = ["amount BETWEEN %s AND %s"]
params = [amount_range[0], amount_range[1]]

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    where_clauses.append("order_date BETWEEN %s AND %s")
    params.append(datetime.combine(start_date, datetime.min.time()))
    params.append(datetime.combine(end_date, datetime.max.time()))

if selected_categories:
    placeholders = ", ".join(["%s"] * len(selected_categories))
    where_clauses.append(f"category IN ({placeholders})")
    params.extend(selected_categories)

if selected_countries:
    placeholders = ", ".join(["%s"] * len(selected_countries))
    where_clauses.append(f"country IN ({placeholders})")
    params.extend(selected_countries)

where_sql = " AND ".join(where_clauses)
query = f"""
    SELECT order_id, customer_name, country, category, product, amount, order_date
    FROM orders
    WHERE {where_sql}
    ORDER BY order_date DESC
    LIMIT 2000
"""

df = run_query(query, params)

col1, col2, col3 = st.columns(3)
col1.metric("Total rows", f"{len(df):,}")
col2.metric("Total revenue", f"€{df['amount'].sum():,.2f}" if not df.empty else "€0.00")
col3.metric("Avg order value", f"€{df['amount'].mean():,.2f}" if not df.empty else "€0.00")

st.caption(f"Τελευταία ενημέρωση: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.dataframe(df, use_container_width=True, hide_index=True)

if not df.empty:
    st.subheader("Έσοδα ανά κατηγορία")
    revenue_by_category = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    st.bar_chart(revenue_by_category)

import streamlit as st
import mysql.connector
import pandas as pd

def get_connection():
    return mysql.connector.connect(
        host="172.16.17.109",
        user="root",
        password="12345",
        database="DAILY_SCHEDULE_AND_DRIVER_DATA"
    )

def get_all_depots():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM TS_ADMIN")
    records = cursor.fetchall()
    df = pd.DataFrame(records)
    cursor.close()
    conn.close()
    return df

# Streamlit UI
st.set_page_config(page_title="Admin Panel", layout="centered")
st.title("🛠️ Depot Admin Panel")

st.markdown("### ✍️ Add or Update Depot Settings")

depot_name = st.text_input("Depot Name")
category = st.selectbox("Depot Type", ["Select Category","Rural", "Urban"])
schedules = st.number_input("Schedules", min_value=0, step=1)
schedules_services = st.number_input("Schedules Services", min_value=0, step=1)
schedules_km = st.number_input("Schedules KM", min_value=0, step=1)

def add_or_update_depot(name, schedules, services, km, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO TS_ADMIN (depot_name, schedules, schedules_services, schedules_km, category)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            schedules = VALUES(schedules),
            schedules_services = VALUES(schedules_services),
            schedules_km = VALUES(schedules_km),
            category = VALUES(category)
    """, (name, schedules, services, km, category))
    conn.commit()
    cursor.close()
    conn.close()

if st.button("Save Depot Settings"):
    if depot_name:
        add_or_update_depot(depot_name, schedules, schedules_services, schedules_km, category)
        st.success(f"✅ Depot '{depot_name}' settings saved.")
    else:
        st.warning("⚠️ Please enter the depot name.")

st.markdown("### 📋 All Depots")
df = get_all_depots()
st.dataframe(df, use_container_width=True)

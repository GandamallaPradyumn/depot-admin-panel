import streamlit as st
import mysql.connector
import pandas as pd

# -----------------------------
# Database Connection Function
# -----------------------------
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["PRADYUMN"]["host"],
        user=st.secrets["root"]["user"],
        password=st.secrets["12345"]["password"],
        database=st.secrets["depot-admin-panel"]["database"]
    )

# -----------------------------
# Fetch All Depot Records
# -----------------------------
def get_all_depots():
    conn = None
    cursor = None
    df = pd.DataFrame()
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM TS_ADMIN")
        records = cursor.fetchall()
        df = pd.DataFrame(records)
    except mysql.connector.Error as err:
        st.error(f"❌ Database error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return df

# -----------------------------
# Insert or Update Depot Record
# -----------------------------
def add_or_update_depot(name, schedules, services, km, category):
    conn = None
    cursor = None
    try:
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
    except mysql.connector.Error as err:
        st.error(f"❌ Failed to save data: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Admin Panel", layout="centered")
st.title("🛠️ Depot Admin Panel")
st.markdown("### ✍️ Add or Update Depot Settings")

# Form Inputs
depot_name = st.text_input("Depot Name")
category = st.selectbox("Depot Type", ["Select Category", "Rural", "Urban"])
schedules = st.number_input("Schedules", min_value=0, step=1)
schedules_services = st.number_input("Schedules Services", min_value=0, step=1)
schedules_km = st.number_input("Schedules KM", min_value=0, step=1)

# Submit Button
if st.button("Save Depot Settings"):
    if not depot_name:
        st.warning("⚠️ Please enter the depot name.")
    elif category == "Select Category":
        st.warning("⚠️ Please select a valid depot type.")
    else:
        add_or_update_depot(depot_name, schedules, schedules_services, schedules_km, category)
        st.success(f"✅ Depot '{depot_name}' settings saved.")

# Display All Depots
st.markdown("### 📋 All Depots")
df = get_all_depots()
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("ℹ️ No depot records found.")


# ---- Import Library ----
import pandas as pd
import numpy as np
import streamlit as st
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime

# ---- Hashing Password Function ----
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---- Get data from ENV ----
uri = st.secrets['uri']

# ---- Create Connection & Save in Session State ----
def init_postgres_connection():
    if "conn" not in st.session_state or st.session_state.conn.closed:
        st.session_state.conn = psycopg2.connect(uri, cursor_factory=RealDictCursor)

# ---- Cretae Register Form ----
def register_user():
    st.title("Register User")

    with st.form("register_form", clear_on_submit=True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register")

    if submitted:
        if not username or not password or not confirm_password:
            st.error("Semua kolom wajib diisi.")
            return

        if password != confirm_password:
            st.error("Password dan Konfirmasi Password tidak sama.")
            return

        # Cek apakah username sudah ada di database
        conn = st.session_state.conn
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            if cur.fetchone() is not None:
                st.error("Username sudah terdaftar, silakan pilih username lain.")
                return

            # Hash password
            hashed_password = hash_password(password)
            now = datetime.datetime.now()

            # Insert data user baru
            cur.execute("""
                INSERT INTO users (username, password, created_at, updated_at, role)
                VALUES (%s, %s, %s, %s, %s)
                """, (username, hashed_password, now, now, 'Government'))
            conn.commit()

            st.success("Registrasi berhasil! Silakan login.")
            st.markdown("[Klik di sini untuk ke halaman login](https://govtalk-gov.streamlit.app/)") 

# Inisialisasi koneksi PostgreSQL sebelum memanggil fungsi register_user
init_postgres_connection()
register_user()

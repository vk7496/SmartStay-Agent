import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

SHEET_ID = "1Kh8Rm-OdWOcA2f24vsN66ClsqVxMigndpCzhVtH85-M"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def get_sheet():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    return sheet

def append_to_sheet(reservation: dict):
    try:
        sheet = get_sheet()
        row = [
            reservation.get("id", ""),
            reservation.get("name", ""),
            reservation.get("phone", ""),
            reservation.get("location", ""),
            reservation.get("nights", ""),
            str(reservation.get("checkin", "")),
            reservation.get("room_type", ""),
            reservation.get("status", "در انتظار تایید"),
            reservation.get("created_at", ""),
        ]
        sheet.append_row(row)
    except Exception as e:
        st.warning(f"خطا در ارسال به Google Sheets: {e}")

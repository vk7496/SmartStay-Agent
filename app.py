import streamlit as st
import pandas as pd
from datetime import datetime

# تنظیمات صفحه
st.set_page_config(page_title="SmartStay-Agent", layout="wide")

# مقداردهی اولیه دیتابیس (در حافظه - بعداً با SQL یا Google Sheets جایگزین کن)
if 'reservations' not in st.session_state:
    st.session_state.reservations = []

# --- توابع کمکی ---
def add_reservation(data):
    data["تاریخ ثبت"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    data["وضعیت"] = "در انتظار تایید"
    st.session_state.reservations.append(data)

# --- طراحی تب‌ها ---
tab1, tab2 = st.tabs(["🏠 ثبت رزرو مسافر", "🔒 پنل مدیریت هاستل"])

# --- تب ۱: مسافر ---
with tab1:
    st.header("سامانه رزرو هوشمند SmartStay")
    with st.form("guest_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("نام و نام خانوادگی")
            phone = st.text_input("شماره تماس")
        with col2:
            location = st.selectbox("شعبه مورد نظر", ["تهران", "اصفهان", "گیلان"])
            nights = st.number_input("تعداد شب", min_value=1, max_value=30)
        
        submitted = st.form_submit_button("ثبت درخواست رزرو")
        if submitted:
            if name and phone:
                add_reservation({"نام": name, "تلفن": phone, "مکان": location, "شب": nights})
                st.success("درخواست شما با موفقیت ثبت شد. به‌زودی با شما تماس می‌گیریم.")
            else:
                st.error("لطفاً تمامی فیلدها را پر کنید.")

# --- تب ۲: مدیریت ---
with tab2:
    # احراز هویت ساده
    password = st.text_input("رمز عبور مدیریت", type="password")
    
    if password == "1234": # رمز عبور دمو
        st.subheader("لیست رزروها")
        
        if st.session_state.reservations:
            df = pd.DataFrame(st.session_state.reservations)
            st.dataframe(df, use_container_width=True)
            
            # بخش عملیات مدیریت
            st.markdown("---")
            st.subheader("عملیات مدیریتی")
            
            # نمایش لیست برای تغییر وضعیت
            for i, res in enumerate(st.session_state.reservations):
                if res["وضعیت"] == "در انتظار تایید":
                    if st.button(f"✅ تایید و ارسال شماره کارت برای {res['نام']}", key=f"btn1_{i}"):
                        st.session_state.reservations[i]["وضعیت"] = "کارت ارسال شد"
                        st.rerun()
                elif res["وضعیت"] == "کارت ارسال شد":
                    if st.button(f"💰 تایید واریز وجه برای {res['نام']}", key=f"btn2_{i}"):
                        st.session_state.reservations[i]["وضعیت"] = "پرداخت شده"
                        st.rerun()
            
            # خروجی اکسل
            st.markdown("---")
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 دانلود گزارش نهایی (CSV)", csv, "reservations.csv", "text/csv")
        else:
            st.info("هنوز رزروی ثبت نشده است.")
    else:
        st.warning("لطفاً رمز عبور را برای مشاهده پنل وارد کنید.")

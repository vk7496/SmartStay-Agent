import streamlit as st
import pandas as pd

# تنظیمات صفحه
st.set_page_config(page_title="مدیریت هوشمند هاستل", layout="wide")

# ۱. مقداردهی اولیه دیتابیس در حافظه (Session State)
if 'rooms' not in st.session_state:
    st.session_state.rooms = pd.DataFrame({
        'شعبه': ['تهران', 'اصفهان', 'گیلان'],
        'ظرفیت خالی': [5, 2, 8],
        'قیمت (تومان)': [500000, 450000, 600000]
    })

if 'logs' not in st.session_state:
    st.session_state.logs = []

# ۲. تابع شبیه‌ساز هوش مصنوعی (اینجا در آینده Ollama قرار می‌گیرد)
def mock_ai_processor(text):
    text = text.lower()
    if "اصفهان" in text:
        return "اصفهان"
    elif "تهران" in text:
        return "تهران"
    elif "گیلان" in text:
        return "گیلان"
    return None

# ۳. طراحی UI
st.title("🏨 پنل مدیریت هوشمند هاستل")
st.markdown("---")

col1, col2 = st.columns([1, 1])

# بخش چت (سمت چپ)
with col1:
    st.subheader("💬 هوش مصنوعی (دریافت رزرو)")
    user_input = st.text_input("پیام مسافر را وارد کنید:", placeholder="مثال: یه اتاق برای اصفهان میخوام")
    
    if st.button("پردازش درخواست"):
        branch = mock_ai_processor(user_input)
        if branch:
            # منطق کاهش ظرفیت
            idx = st.session_state.rooms.index[st.session_state.rooms['شعبه'] == branch][0]
            if st.session_state.rooms.loc[idx, 'ظرفیت خالی'] > 0:
                st.session_state.rooms.loc[idx, 'ظرفیت خالی'] -= 1
                st.session_state.logs.append(f"رزرو برای شعبه {branch} ثبت شد.")
                st.success(f"رزرو در شعبه {branch} با موفقیت انجام شد!")
            else:
                st.error("ظرفیت تکمیل است!")
        else:
            st.warning("لطفاً نام شعبه (تهران، اصفهان، گیلان) را واضح‌تر بنویسید.")

# بخش داشبورد (سمت راست)
with col2:
    st.subheader("📊 وضعیت لحظه‌ای شعب")
    st.table(st.session_state.rooms)
    
    st.subheader("📝 تاریخچه رزروها")
    for log in st.session_state.logs:
        st.write(f"✅ {log}")

# دکمه ریست برای دمو
if st.sidebar.button("ریست دمو"):
    st.session_state.rooms = pd.DataFrame({
        'شعبه': ['تهران', 'اصفهان', 'گیلان'],
        'ظرفیت خالی': [5, 2, 8],
        'قیمت (تومان)': [500000, 450000, 600000]
    })
    st.session_state.logs = []
    st.rerun()

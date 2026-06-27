import streamlit as st
import pandas as pd
import re
import os
from datetime import date, timedelta
from src.database import init_db, add_reservation, get_all_reservations, update_status
from src.sheets_sync import append_to_sheet

# ─── راه‌اندازی ───────────────────────────────────────────────────────────────
init_db()

st.set_page_config(
    page_title="SmartStay | سامانه رزرو هوشمند",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── استایل سفارشی ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600;700&display=swap');

* { font-family: 'Vazirmatn', sans-serif !important; direction: rtl; }

.main-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white;
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    text-align: center;
}
.main-header h1 { font-size: 2rem; margin: 0; letter-spacing: -0.5px; }
.main-header p  { font-size: 0.9rem; opacity: 0.7; margin: 0.4rem 0 0; }

.badge-pending  { background:#fff3cd; color:#856404; border-radius:20px; padding:3px 10px; font-size:0.78rem; }
.badge-sent     { background:#cff4fc; color:#055160; border-radius:20px; padding:3px 10px; font-size:0.78rem; }
.badge-paid     { background:#d1e7dd; color:#0a3622; border-radius:20px; padding:3px 10px; font-size:0.78rem; }

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0f3460, #533483) !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
    width: 100% !important;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── هدر ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏠 SmartStay</h1>
    <p>سامانه رزرو هوشمند هاستل | ثبت سریع، تایید آنلاین</p>
</div>
""", unsafe_allow_html=True)

# ─── تب‌ها ────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🛏️  ثبت رزرو مسافر", "🔐  پنل مدیریت"])

# ══════════════════════════════════════════════════
# تب ۱ — فرم مسافر
# ══════════════════════════════════════════════════
with tab1:
    with st.form("guest_form", clear_on_submit=True):
        st.subheader("اطلاعات رزرو")

        c1, c2 = st.columns([2, 1])
        with c1:
            name = st.text_input("نام و نام خانوادگی *", placeholder="مثال: علی رضایی")
        with c2:
            phone = st.text_input("شماره تماس *", placeholder="09xxxxxxxxx")

        c3, c4, c5 = st.columns(3)
        with c3:
            location = st.selectbox("شعبه مورد نظر", ["تهران", "اصفهان", "گیلان"])
        with c4:
            checkin = st.date_input("تاریخ ورود", value=date.today() + timedelta(days=1), min_value=date.today())
        with c5:
            nights = st.number_input("تعداد شب", min_value=1, max_value=30, step=1, value=1)

        room_type = st.radio(
            "نوع اتاق",
            ["تخت دورمیتوری (مشترک)", "اتاق دو نفره (خصوصی)", "اتاق یک نفره"],
            horizontal=True,
        )

        notes = st.text_area("توضیحات اضافه (اختیاری)", placeholder="درخواست خاص، زمان ورود، ...", height=80)

        submitted = st.form_submit_button("✅  ثبت درخواست رزرو", type="primary")

    if submitted:
        errors = []
        if not name.strip():
            errors.append("نام و نام خانوادگی را وارد کنید.")
        if not re.match(r'^09\d{9}$', phone.strip()):
            errors.append("شماره تماس باید با ۰۹ شروع شود و ۱۱ رقم باشد.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            checkout = checkin + timedelta(days=int(nights))
            add_reservation(
                name.strip(), phone.strip(), location, int(nights),
                checkin=checkin, room_type=room_type, notes=notes,
            )
            append_to_sheet({
                "name": name.strip(),
                "phone": phone.strip(),
                "location": location,
                "nights": int(nights),
                "checkin": checkin,
                "room_type": room_type,
                "status": "در انتظار تایید",
            })
            st.success(f"✅ رزرو شما برای **{name.strip()}** در شعبه **{location}** ثبت شد.")
            st.info(f"📅 تاریخ ورود: {checkin}  |  خروج: {checkout}  |  {nights} شب")
            st.caption("پس از بررسی، کارت پرداخت برای شما ارسال می‌شود.")

# ══════════════════════════════════════════════════
# تب ۲ — پنل مدیریت
# ══════════════════════════════════════════════════
with tab2:
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", st.secrets.get("ADMIN_PASSWORD", "smartstay2025"))

    pwd_col, _ = st.columns([1, 2])
    with pwd_col:
        password = st.text_input("رمز عبور مدیریت", type="password", placeholder="رمز عبور را وارد کنید")

    if not password:
        st.info("لطفاً رمز عبور را برای مشاهده پنل وارد کنید.")

    elif password != ADMIN_PASSWORD:
        st.error("❌ رمز عبور اشتباه است!")

    else:
        st.success("✅ وارد پنل مدیریت شدید.")
        st.markdown("---")

        data = get_all_reservations()

        if not data:
            st.info("هنوز هیچ رزروی ثبت نشده است.")
        else:
            df = pd.DataFrame(data)

            # ─── آمار سریع ───────────────────────────────────
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("کل رزروها", len(df))
            m2.metric("در انتظار تایید", len(df[df["status"] == "در انتظار تایید"]) if "status" in df.columns else "—")
            m3.metric("کارت ارسال شد", len(df[df["status"] == "کارت ارسال شد"]) if "status" in df.columns else "—")
            m4.metric("پرداخت شده", len(df[df["status"] == "پرداخت شده"]) if "status" in df.columns else "—")

            st.markdown("---")

            # ─── فیلتر ───────────────────────────────────────
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filter_location = st.selectbox("فیلتر شعبه", ["همه"] + list(df["location"].unique()) if "location" in df.columns else ["همه"])
            with col_f2:
                filter_status = st.selectbox("فیلتر وضعیت", ["همه", "در انتظار تایید", "کارت ارسال شد", "پرداخت شده"])

            filtered = df.copy()
            if filter_location != "همه" and "location" in df.columns:
                filtered = filtered[filtered["location"] == filter_location]
            if filter_status != "همه" and "status" in df.columns:
                filtered = filtered[filtered["status"] == filter_status]

            # ─── جدول با ستون‌های فارسی ──────────────────────
            cols = ["name", "phone", "location", "nights", "checkin", "room_type", "status", "created_at"]
            cols = [c for c in cols if c in filtered.columns]
            st.dataframe(
                filtered[cols].rename(columns={
                    "name": "نام",
                    "phone": "تلفن",
                    "location": "شعبه",
                    "nights": "شب",
                    "checkin": "تاریخ ورود",
                    "room_type": "نوع اتاق",
                    "status": "وضعیت",
                    "created_at": "ثبت شده",
                }),
                use_container_width=True,
                height=280,
            )

            # ─── تغییر وضعیت ─────────────────────────────────
            st.markdown("### مدیریت وضعیت رزروها")

            for res in data:
                c_info, c_btn = st.columns([3, 1])
                with c_info:
                    status = res.get("status", "")
                    badge_class = {
                        "در انتظار تایید": "badge-pending",
                        "کارت ارسال شد": "badge-sent",
                        "پرداخت شده": "badge-paid",
                    }.get(status, "badge-pending")
                    st.markdown(
                        f"**{res.get('name','')}** — {res.get('location','')} — {res.get('nights','')} شب  "
                        f"<span class='{badge_class}'>{status}</span>",
                        unsafe_allow_html=True,
                    )
                with c_btn:
                    if status == "در انتظار تایید":
                        if st.button("✅ تایید", key=f"app_{res['id']}"):
                            update_status(res["id"], "کارت ارسال شد")
                            st.rerun()
                    elif status == "کارت ارسال شد":
                        if st.button("💰 واریز شد", key=f"pay_{res['id']}"):
                            update_status(res["id"], "پرداخت شده")
                            st.rerun()
                    else:
                        st.caption("✔ تکمیل شده")

            st.markdown("---")

            # ─── دانلود CSV ──────────────────────────────────
            csv_df = df[cols].rename(columns={
                "name": "نام",
                "phone": "تلفن",
                "location": "شعبه",
                "nights": "شب",
                "checkin": "تاریخ ورود",
                "room_type": "نوع اتاق",
                "status": "وضعیت",
                "created_at": "ثبت شده",
            })
            csv = csv_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 دانلود گزارش CSV",
                data=csv,
                file_name="smartstay_report.csv",
                mime="text/csv",
            )

import streamlit as st
from streamlit_folium import st_folium
import folium
import sqlite3
import pandas as pd

# --- إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('clients_manager.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            appointment TEXT,
            lat REAL,
            lon REAL,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- واجهة التطبيق ---
st.set_page_config(page_title="مدير العملاء", layout="wide")
st.title("🗂️ نظام تسجيل العملاء والمواقع")

# مدخلات البيانات
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("📝 إضافة عميل جديد")
    name = st.text_input("اسم العميل")
    phone = st.text_input("رقم الهاتف")
    date = st.date_input("موعد الزيارة")
    notes = st.text_area("ملاحظات")

with col2:
    st.subheader("📍 حدد الموقع على الخريطة")
    m = folium.Map(location=[30.0444, 31.2357], zoom_start=12)
    map_data = st_folium(m, width=500, height=300)
    
    lat, lon = None, None
    if map_data["last_clicked"]:
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        st.info(f"تم تحديد الإحداثيات: {lat:.4f}, {lon:.4f}")

if st.button("حفظ البيانات"):
    if name and lat:
        conn = sqlite3.connect('clients_manager.db')
        c = conn.cursor()
        c.execute('INSERT INTO customers (name, phone, appointment, lat, lon, notes) VALUES (?, ?, ?, ?, ?, ?)',
                  (name, phone, str(date), lat, lon, notes))
        conn.commit()
        conn.close()
        st.success(f"تم حفظ {name} بنجاح! ✅")
    else:
        st.error("الرجاء إدخال الاسم وتحديد الموقع.")

# --- البحث والعرض ---
st.divider()
st.subheader("🔍 البحث في السجلات")
search = st.text_input("ابحث بالاسم أو الرقم:")

conn = sqlite3.connect('clients_manager.db')
if search:
    query = f"SELECT * FROM customers WHERE name LIKE '%{search}%' OR phone LIKE '%{search}%'"
else:
    query = "SELECT * FROM customers ORDER BY id DESC"
df = pd.read_sql_query(query, conn)
conn.close()

if not df.empty:
    # إضافة رابط خرائط جوجل
    df['رابط الموقع'] = df.apply(lambda r: f"https://www.google.com/maps?q={r['lat']},{r['lon']}", axis=1)
    
    # تحسين شكل الجدول
    st.dataframe(
        df[['name', 'phone', 'appointment', 'notes', 'رابط الموقع']],
        column_config={"رابط الموقع": st.column_config.LinkColumn("فتح في خرائط جوجل")},
        use_container_width=True,
        hide_index=True
    )

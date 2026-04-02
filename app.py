import streamlit as st
import pandas as pd
import sqlite3
import folium
from streamlit_folium import st_folium

# --- 1. إعدادات قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('customers.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS customers
                 (name TEXT, phone TEXT, appointment TEXT, notes TEXT, 
                  lat REAL, lon REAL, location_url TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. نظام التنقل بالأزرار ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'إضافة'

st.title("📂 نظام إدارة العملاء والمواقع")

# إنشاء صف الأزرار في الأعلى
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("➕ إضافة عميل جديد", use_container_width=True):
        st.session_state.current_page = 'إضافة'
with col_nav2:
    if st.button("📋 قائمة العملاء", use_container_width=True):
        st.session_state.current_page = 'قائمة'

st.divider()

# --- 3. صفحة إضافة عميل جديد ---
if st.session_state.current_page == 'إضافة':
    st.header("📍 تسجيل موقع عميل")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        name = st.text_input("اسم العميل")
        phone = st.text_input("رقم الهاتف")
        date = st.date_input("موعد الزيارة")
        notes = st.text_area("ملاحظات إضافية")

    with col2:
        st.write("حدد الموقع على الخريطة 👇")
        m = folium.Map(location=[30.0444, 31.2357], zoom_start=10)
        m.add_child(folium.LatLngPopup())
        map_data = st_folium(m, height=300, width=400)

    # استخراج الإحداثيات عند الضغط
    lat, lon = None, None
    if map_data and map_data.get('last_clicked'):
        lat = map_data['last_clicked']['lat']
        lon = map_data['last_clicked']['lng']
        st.success(f"تم تحديد الإحداثيات: {lat:.4f}, {lon:.4f}")

    if st.button("حفظ البيانات ✅"):
        if name and lat:
            google_maps_url = f"https://www.google.com/maps?q={lat},{lon}"
            conn = sqlite3.connect('customers.db')
            c = conn.cursor()
            c.execute("INSERT INTO customers VALUES (?,?,?,?,?,?,?)", 
                      (name, phone, str(date), notes, lat, lon, google_maps_url))
            conn.commit()
            conn.close()
            st.balloons()
            st.success(f"تم حفظ بيانات {name} بنجاح!")
        else:
            st.error("يرجى إدخال الاسم وتحديد الموقع على الخريطة!")

# --- 4. صفحة قائمة العملاء ---
elif st.session_state.current_page == 'قائمة':
    st.header("📋 سجل العملاء")
    
    conn = sqlite3.connect('customers.db')
    df = pd.read_sql_query("SELECT name, phone, appointment, notes, location_url FROM customers", conn)
    conn.close()

    if not df.empty:
        # إحصائية سريعة
        st.metric("إجمالي العملاء", len(df))
        
        # خانة البحث
        search = st.text_input("🔍 ابحث عن اسم العميل:")
        if search:
            df = df[df['name'].str.contains(search, case=False, na=False)]
        
        # عرض الجدول التفاعلي
        st.dataframe(
            df,
            column_config={
                "location_url": st.column_config.LinkColumn("موقع جوجل 📍"),
                "name": "الاسم",
                "phone": "الهاتف",
                "appointment": "التاريخ",
                "notes": "الملاحظات"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("لا توجد بيانات مسجلة بعد.")

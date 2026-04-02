import streamlit as st
import pandas as pd
import sqlite3
from streamlit_js_eval import get_geolocation
# --- 1. إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('customers.db')
    c = conn.cursor()
    # أنشأنا الجدول بحيث يكون "الاسم" هو المرجع الأساسي للتعديل
    c.execute('''CREATE TABLE IF NOT EXISTS customers
                 (name TEXT PRIMARY KEY, phone TEXT, appointment TEXT, notes TEXT, 
                  lat REAL, lon REAL, location_url TEXT)''')
    conn.commit()
    conn.close()
init_db()
# --- 2. نظام التنقل بالأزرار ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'إضافة'
st.title("📂 نظام إدارة العملاء الذكي")
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("➕ إضافة عميل جديد", use_container_width=True):
        st.session_state.current_page = 'إضافة'
with col_nav2:
    if st.button("📋 قائمة وتعديل العملاء", use_container_width=True):
        st.session_state.current_page = 'قائمة'
st.divider()
# --- 3. صفحة الإضافة ---
if st.session_state.current_page == 'إضافة':
    st.header("📍 تسجيل عميل في الموقع الحالي")
    
    # جلب الموقع التلقائي عبر المتصفح
    loc = get_geolocation()
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("اسم العميل")
        phone = st.text_input("رقم الهاتف")
    
    with col2:
        date = st.date_input("موعد الزيارة")
        notes = st.text_area("ملاحظات", height=68)
    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        google_url = f"https://www.google.com/maps?q={lat},{lon}"
        
        st.success("✅ تم تحديد موقعك الحالي")
        st.markdown(f"🔗 [تأكد من موقعك على خرائط جوجل]({google_url})")
        
        if st.button("حفظ البيانات ✅", use_container_width=True):
            if name:
                try:
                    conn = sqlite3.connect('customers.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO customers (name, phone, appointment, notes, lat, lon, location_url) VALUES (?,?,?,?,?,?,?)", 
                              (name, phone, str(date), notes, lat, lon, google_url))
                    conn.commit()
                    conn.close()
                    st.balloons()
                    st.success(f"تم حفظ {name} بنجاح!")
                except sqlite3.IntegrityError:
                    st.error("⚠️ هذا الاسم مسجل مسبقاً، يرجى استخدام اسم مختلف أو تعديله من القائمة.")
            else:
                st.error("يرجى إدخال اسم العميل")
    else:
        st.warning("🔄 جاري طلب إذن الموقع... يرجى الموافقة في المتصفح.")
# --- 4. صفحة القائمة والتعديل المباشر ---
elif st.session_state.current_page == 'قائمة':
    st.header("📋 سجل العملاء القابل للتعديل")
    
    conn = sqlite3.connect('customers.db')
    df = pd.read_sql_query("SELECT name, phone, appointment, notes, location_url FROM customers", conn)
    conn.close()
    if not df.empty:
        st.info("💡 يمكنك تعديل أي خانة (الاسم، الهاتف، الملاحظات) مباشرة من الجدول ثم الضغط على حفظ.")
        
        # محرر البيانات التفاعلي
        edited_df = st.data_editor(
            df,
            column_config={
                "location_url": st.column_config.LinkColumn("الخريطة 📍", display_text="فتح"),
                "name": "الاسم",
                "phone": "الهاتف",
                "appointment": "التاريخ",
                "notes": "الملاحظات"
            },
            hide_index=True,
            use_container_width=True,
            key="client_editor"
        )
        if st.button("💾 حفظ جميع التعديلات", use_container_width=True):
            try:
                conn = sqlite3.connect('customers.db')
                # نقوم باستبدال الجدول القديم بالبيانات الجديدة التي عدلتها في الجدول
                edited_df.to_sql('customers', conn, if_exists='replace', index=False)
                conn.close()
                st.success("✅ تم تحديث قاعدة البيانات بنجاح!")
                st.rerun()
            except Exception as e:
                st.error(f"حدث خطأ أثناء الحفظ: {e}")
    else:
        st.info("السجل فارغ حالياً.")

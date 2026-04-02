if search:
            df = df[df['name'].str.contains(search, case=False, na=False)]
        
        st.dataframe(
            df,
            column_config={
                "location_url": st.column_config.LinkColumn("موقع جوجل 📍"),
                "name": "الاسم", "phone": "الهاتف", "appointment": "التاريخ", "notes": "الملاحظات"
            },
            hide_index=True, use_container_width=True
        )
    else:
        st.info("لا توجد بيانات مسجلة بعد.")

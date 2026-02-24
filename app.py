if st.session_state.bakul:
        st.write("### 🛒 Bakul Sementara")
        
        # Papar setiap item dengan butang padam
        for index, item in enumerate(st.session_state.bakul):
            col_ubat, col_qty, col_padam = st.columns([3, 1, 1])
            col_ubat.write(f"**{item['u']}**")
            col_qty.write(f"{item['q']}")
            
            # Jika butang dipadam tekan, buang item dari list berdasarkan index
            if col_padam.button("🗑️", key=f"del_{index}"):
                st.session_state.bakul.pop(index)
                st.rerun()

        st.divider()
        if st.button("💾 SIMPAN SEMUA", type="primary"):
            payload = {
                "Nama": nama, "IC": ic, "TCA_Ubat": str(t_u), 
                "TCA_Clinic": str(t_d) if t_d else "-",
                "Ubat_List": " | ".join([x['u'] for x in st.session_state.bakul]),
                "Kuantiti": " | ".join([x['q'] for x in st.session_state.bakul]),
                "Batch": batch
            }
            requests.post(URL_API, json=payload)
            st.success("Data Berhasil Disimpan!"); st.session_state.bakul = []; st.balloons()

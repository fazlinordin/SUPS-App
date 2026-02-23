def convert_to_matrix_with_total(df_filtered):
    rows = []
    for _, row in df_filtered.iterrows():
        ubats = str(row['UBAT_LIST']).split(' | ')
        qtys = str(row['KUANTITI']).split(' | ')
        for u, q in zip(ubats, qtys):
            rows.append({
                'NAMA PESAKIT': row['NAMA'],
                'UBAT': u.strip(),
                'KUANTITI': q.strip(),
                'NILAI': ekstrak_angka(q)
            })
    
    if not rows:
        return pd.DataFrame()
        
    new_df = pd.DataFrame(rows)
    
    # 1. Buat Matrix Utama
    matrix = new_df.pivot_table(index='UBAT', columns='NAMA PESAKIT', values='KUANTITI', aggfunc='first').fillna('')
    
    # --- TAMBAH BARIS INI UNTUK SUSUN IKUT ABJAD ---
    matrix = matrix.sort_index(ascending=True) 
    # ----------------------------------------------

    # 2. Kira Jumlah Besar (Total) setiap ubat
    total_series = new_df.groupby('UBAT')['NILAI'].sum()
    
    # 3. Masukkan Kolum TOTAL di posisi pertama
    matrix.insert(0, 'TOTAL (BIJI)', total_series)
    
    return matrix

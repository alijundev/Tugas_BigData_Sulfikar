import sqlite3
import json
import os
import re
import html
import pandas as pd
from datetime import datetime

# fungsi berishkan file
def bersihkan_html(raw_html):
    # Ubah entitas HTML (seperti &nbsp;) menjadi karakter asli
    text = html.unescape(raw_html)
    text = text.replace('\xa0', ' ').replace('&nbsp;', ' ')
    # Hapus semua tag HTML (seperti <p>, <li>, <strong>, dll)
    text = re.sub(r'<[^>]+>', ' ', text)
    # Hapus spasi ganda, tab, dan enter/newline agar teks menjadi satu baris rata
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

#Konversi Unix Timestamp menjadi Tanggal Normal (YYYY-MM-DD)
def ubah_timestamp(unix_time):
    try:
        return datetime.fromtimestamp(int(unix_time)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return unix_time

# 1. EXTRACT & TRANSFORM: Data Tidak Terstruktur (TXT)
txt_data = []
txt_dir = 'raw_dataset/Data_Tidak_Terstruktur/data/'

print("Membaca dan file TXT...")
for filename in os.listdir(txt_dir):
    if filename.endswith(".txt"):
        job_id = filename.replace('.txt', '')
        
        with open(os.path.join(txt_dir, filename), 'r', encoding='utf-8') as f:
            isi = f.read()
        
        isi_bersih = bersihkan_html(isi)
        
        txt_data.append({"Job_ID": job_id, "Deskripsi_Teks": isi_bersih})

df_txt = pd.DataFrame(txt_data)

# 2. EXTRACT: Data Terstruktur (SQLite)

# Buat koneksi database sementara di dalam RAM (in-memory)
temp_conn = sqlite3.connect(':memory:')
temp_cursor = temp_conn.cursor()

with open('raw_dataset/Data_Terstruktur/lowongan.sql', 'r', encoding='utf-8') as f:
    sql_script = f.read()

temp_cursor.executescript(sql_script)
df_sql = pd.read_sql_query("SELECT * FROM tabel_lowongan", temp_conn)
temp_conn.close()

df_sql['Tanggal_Posting'] = df_sql['Tanggal_Posting'].apply(ubah_timestamp)

# 3. EXTRACT & TRANSFORM: Data Semi-Terstruktur (JSON)
print("Membaca dan me-meratakan array JSON...")
with open('raw_dataset/Data_Semi_Terstruktur/metadata_lowongan.json', 'r', encoding='utf-8') as f:
    data_json = json.load(f)

df_json = pd.DataFrame(data_json)
# Flattening: Mengubah format list/array menjadi string
df_json['Kebutuhan_Skill'] = df_json['Kebutuhan_Skill'].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
df_json['Kategori_Kontrak'] = df_json['Kategori_Kontrak'].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)

# 4. Menggabungkan Ketiga Data Berdasarkan Job_ID
print("Menggabungkan ketiga format data (JOIN)...")
df_merge = pd.merge(df_sql, df_json, on='Job_ID', how='inner')
df_final = pd.merge(df_merge, df_txt, on='Job_ID', how='inner')


# 5. Simpan ke satu file CSV
output_file = 'final_dataset/Final_Dataset_Lowongan.csv'
df_final.to_csv(output_file, index=False, encoding='utf-8')
print(f"SELESAI! Data berhasil disatukan dan disimpan di: {output_file}")
import requests
import sqlite3
import os

os.makedirs('raw_dataset/Data_Terstruktur', exist_ok=True)
# 1. Ambil data riil dari API Job Board publik
jobs_data = []
for i in range(1,6):
    url = f"https://www.arbeitnow.com/api/job-board-api?page={i}"
    # print(url)
    print(f"Menghubungi {url}...")
    response = requests.get(url)

    if response.status_code == 200:
        jobs_data +=  response.json()['data']
    else:
        print("Gagal mengambil data.")
        exit()

# 2. Siapkan Database SQLite (Data Terstruktur)
db_path = 'raw_dataset/Data_Terstruktur/lowongan.sqlite'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 3. Buat Tabel SQL (Hanya ambil atribut terstruktur)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tabel_lowongan (
        Job_ID TEXT PRIMARY KEY,
        Perusahaan TEXT,
        Jabatan TEXT,
        Lokasi TEXT,
        Remote BOOLEAN,
        Tanggal_Posting TEXT
    )
''')

# Kosongkan tabel jika script dijalankan ulang agar tidak duplikat
cursor.execute('DELETE FROM tabel_lowongan')

# 4. Filter dan Masukkan Data ke SQLite
sql_data = []
for job in jobs_data:
    # Mengambil ID unik, nama perusahaan, judul, dan data biner/waktu
    job_id = job.get('slug')
    company = job.get('company_name')
    title = job.get('title')
    location = job.get('location')
    is_remote = job.get('remote')
    created_at = job.get('created_at')
    
    sql_data.append((job_id, company, title, location, is_remote, created_at))

# Insert massal ke database
cursor.executemany('''
    INSERT OR IGNORE INTO tabel_lowongan (Job_ID, Perusahaan, Jabatan, Lokasi, Remote, Tanggal_Posting)
    VALUES (?, ?, ?, ?, ?, ?)
''', sql_data)

conn.commit()

print(f"Data Terstruktur berhasil disimpan di: {db_path}")

with open('raw_dataset/Data_Terstruktur/lowongan.sql', 'w') as f:
    for baris_perintah in conn.iterdump():
        f.write(f'{baris_perintah}\n')

conn.close()
print("Selesai! File .sqlite dan teks .sql berhasil dibuat.")
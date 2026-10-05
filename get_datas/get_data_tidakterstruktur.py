import requests
import os
import re
import html
# 1. Pastikan folder tersedia
os.makedirs('raw_dataset/Data_Tidak_Terstruktur', exist_ok=True)

# 2. Ambil data riil dari API
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


# 3. Ekstrak dan simpan deskripsi ke dalam banyak file TXT
count = 0
for job in jobs_data:
    job_id = job.get('slug')
    deskripsi_mentah = job.get('description', '')
    
    
    # Simpan ke file TXT dengan nama file = Job_ID
    file_path = f"raw_dataset/Data_Tidak_Terstruktur/data/{job_id}.txt"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(deskripsi_mentah)
    
    count += 1

print(f"Berhasil! {count} file TXT deskripsi kerja tersimpan di folder: Data_Tidak_Terstruktur/")
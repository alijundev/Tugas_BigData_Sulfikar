import requests
import json
import os

# 1. Pastikan folder tersedia
os.makedirs('raw_dataset/Data_Semi_Terstruktur', exist_ok=True)

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

semi_structured_data = []

for job in jobs_data:
    job_id = job.get('slug')
    
    # Mengambil list/array dari tag dan tipe pekerjaan
    tags = job.get('tags', [])
    job_types = job.get('job_types', [])
    
    # Menyusun bentuk data semi-terstruktur
    metadata = {
        "Job_ID": job_id,
        "Kebutuhan_Skill": tags,
        "Kategori_Kontrak": job_types
    }
    semi_structured_data.append(metadata)
json_path = "raw_dataset/Data_Semi_Terstruktur/metadata_lowongan.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(semi_structured_data,f, indent=4, ensure_ascii=False)

print(f"Berhasil! {len(semi_structured_data)} data JSON tersimpan di: {json_path}")
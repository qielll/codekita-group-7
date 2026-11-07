# CodeKita — Platform Belajar Adaptif Blockly-ke-Python (MVP)

Siswa menyeret blok visual → blok tersebut menjadi kode Python → kode
dinilai secara otomatis di dalam sandbox → tingkat penguasaan per konsep
diperbarui → latihan berikutnya yang sedikit lebih sulit/mudah
direkomendasikan. Kontrak cakupan: lihat `MVP_SPEC.md`. Arsitektur dan
aturan adaptifnya: lihat `ARCHITECTURE.md`.

## Prasyarat
- **Docker** (wajib untuk sandbox penilai — tidak ada fallback non-Docker
  untuk demo)
- Python 3.12+, Node 20+

## Cara Menjalankan
```bash
# 1) Image sandbox
docker build -t codekita-sandbox:latest -f grader/sandbox.Dockerfile grader/

# 2) API penilai (terminal 1)
pip install -r grader/requirements.txt
uvicorn grader.main:app --port 8000        # dari root repo

# 3) Aplikasi web (terminal 2)
cd web && npm install && npm run dev       # http://localhost:5173
```

## Pengujian
```bash
pip install fastapi uvicorn pydantic httpx pytest
python -m pytest tests/ -q
# Di mesin tanpa Docker, pengujian menggunakan sandbox lokal khusus pengembangan:
CODEKITA_ALLOW_LOCAL_SANDBOX=1 python -m pytest tests/ -q
```

## Menambah Pelajaran
1. Tambahkan `content/lessons/<id>.json` (penjelasan, contoh yang dikerjakan, id latihan).
2. Tambahkan/perluas `content/exercises/<concept>.json` dengan soal dan
   kasus uji tersembunyi (`expected_stdout` per kasus). Tidak perlu mengubah kode.

## Skrip Demo (5 menit)
1. Buka aplikasi web, masukkan nama/kode kelas (tanpa kata sandi).
2. Pelajaran 1 → buat *First / Second* dengan dua blok print → lihat
   pratinjau Python yang muncul → **Run & Grade** → umpan balik lulus yang ramah.
3. Kirim solusi yang salah → hasil gagal yang ramah, tanpa stack trace.
4. (Terminal penilai / API) kirim `while True: pass` → kode dihentikan pada
   batas 2 detik dan dilaporkan sebagai timeout; server tetap berjalan.
5. Gagal pada latihan loops dua kali → panel Progress menunjukkan penguasaan
   loops menurun dan loops tetap menjadi konsep yang direkomendasikan ⭐; lulus dua kali →
   tingkat kesulitan naik dan jalur belajar berlanjut.

# 2026 Dashboard Riset — LAO

Website satu halaman: **Publikasi (otomatis dari SINTA)**, **Status Bimbingan (manual)**, dan **Topik TA yang Ditawarkan (manual)**.
Di-host di Netlify, tersambung ke repo GitHub ini.

## Struktur

```
index.html                          → halaman dashboard
data/publications.json              → publikasi  (OTOMATIS, jangan diedit manual)
data/topik.json                     → topik TA   (MANUAL — edit di sini)
data/bimbingan.json                 → bimbingan  (MANUAL — edit di sini)
scripts/scrape_sinta.py             → skrip ambil data SINTA
.github/workflows/update-sinta.yml  → penjadwal otomatis publikasi
```

Setiap file di-commit → Netlify otomatis deploy ulang → website ter-update.

---

## ✏️ CARA EDIT TOPIK YANG DITAWARKAN  (`data/topik.json`)

1. Buka repo → folder `data` → klik **`topik.json`** → klik ikon pensil (Edit).
2. Isinya daftar topik. Satu topik = satu blok `{ ... }`:

```json
{
 "no": 1,
 "kbk": "Instrumentasi, Kontrol, IoT (AUR)",
 "topik": "Judul topik lengkap di sini",
 "kualifikasi": ["1. syarat pertama", "2. syarat kedua"],
 "catatan": "catatan singkat",
 "ec": "Ya"
}
```

- **kbk** hanya dua pilihan (tulis persis):
  `"Instrumentasi, Kontrol, IoT (AUR)"` atau `"Sinyal, Citra (DZI)"`
- **ec** (Ethical Clearance): `"Ya"` atau `"Tidak"`
- **no**: nomor urut dalam kategori itu.

**Menambah topik:** salin satu blok `{...}`, tempel setelahnya, beri koma pemisah, ubah isinya.
**Menghapus topik:** hapus satu blok `{...}` beserta koma-nya.

⚠️ Perhatikan koma: antar-blok dipisah koma, blok terakhir TANPA koma.

3. Scroll bawah → **Commit changes**. Selesai — website update ±1 menit.

---

## ✏️ CARA EDIT STATUS BIMBINGAN  (`data/bimbingan.json`)

Struktur: dikelompokkan `berjalan` / `selesai`, lalu per prodi (`bme` = Teknik Biomedis, `tel` = Teknik Telekomunikasi).

```json
{
 "berjalan": {
   "bme": [ {"nama":"Nama Mhs","judul":"Judul TA"} ]
 },
 "selesai": {
   "bme": [ {"nama":"Nama Mhs","judul":"Judul TA"} ],
   "tel": { "judul":"Judul tim (1 judul)", "mhs":[ {"nama":"A"}, {"nama":"B"} ] }
 }
}
```

- **bme** = daftar mahasiswa, tiap orang `{"nama":"...","judul":"..."}`.
- **tel** = satu judul tim + daftar nama (`mhs`).
- Untuk menambah mahasiswa berjalan Telekomunikasi, tambahkan `"tel"` di dalam `"berjalan"` dengan pola sama seperti selesai.

Menambah/menghapus = tambah/hapus blok `{...}` di dalam daftar, jaga koma.

---

## 📚 PUBLIKASI — OTOMATIS (jangan edit manual)

`data/publications.json` diperbarui otomatis oleh GitHub Actions dari profil SINTA
(ID `6973450`), dijadwalkan tiap **Senin 05:00 WIB**.

- Jalankan manual: tab **Actions** → **Update publikasi dari SINTA** → **Run workflow**.
- Aktifkan sekali: tab **Actions** → **I understand... enable workflows**.
- Bila SINTA memblokir sesekali, jalankan ulang; data lama tetap aman (tidak ditimpa saat gagal).

---

## Catatan aman

- Semua data juga tertanam sebagai cadangan di `index.html`, jadi halaman tetap tampil
  walau file JSON gagal dimuat. File JSON hanya "menimpa" saat berhasil dibaca.
- Validasi JSON sebelum commit (mis. paste ke jsonlint.com) untuk menghindari salah koma.

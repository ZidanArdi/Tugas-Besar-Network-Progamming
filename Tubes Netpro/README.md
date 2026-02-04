# WiFi Scanner - Zidan Ardiansyah

Aplikasi WiFi Scanner dengan GUI menggunakan Python dan Tkinter.

## Struktur Folder

```
📁 Tubes Netpro/
├── 📁 src/                     # Source code
│   └── wifi_scanner_gui.py     # File utama aplikasi
├── 📁 dist/                    # Hasil build (.exe file)
├── 📁 docs/                    # Dokumentasi dan hasil scan
│   └── wifi_scan_hasil.txt     # Contoh hasil scan
├── 📁 build/                   # Temporary build files (auto-generated)
├── build_exe.py                # Script untuk build exe
├── requirements.txt            # Python dependencies
├── WiFi_Scanner_Zidan.spec     # PyInstaller spec file
└── README.md                   # File ini
```

## Cara Menjalankan

### Menjalankan dari Source Code

```bash
python src/wifi_scanner_gui.py
```

### Menjalankan EXE

Setelah build, jalankan file `WiFi_Scanner_Zidan.exe` di folder `dist/`

## Cara Build EXE

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Jalankan Build Script

```bash
python build_exe.py
```

### 3. Hasil Build

File EXE akan tersedia di folder `dist/WiFi_Scanner_Zidan.exe`

## Features

- Scan jaringan WiFi yang tersedia
- Deteksi kekuatan sinyal
- Informasi keamanan WiFi
- Export hasil scan
- GUI yang user-friendly

## Requirements

- Python 3.x
- tkinter (biasanya sudah termasuk dalam Python)
- PyInstaller (untuk build exe)

## Author

Zidan Ardiansyah

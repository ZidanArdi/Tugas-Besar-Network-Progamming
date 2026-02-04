# build_exe.py
# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import shutil
import io

# Set stdout encoding ke utf-8 untuk mendukung emoji
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def clean_build_folders():
    """Hapus folder build dan dist sebelumnya"""
    folders_to_remove = ['build', 'dist']
    
    for folder in folders_to_remove:
        if os.path.exists(folder):
            print(f"🗑️  Menghapus folder {folder}...")
            shutil.rmtree(folder)

def build_exe():
    """Buat executable dengan PyInstaller"""
    print("🚀 Membangun aplikasi EXE...")
    print("=" * 50)
    
    # Nama file utama
    main_script = "src/wifi_scanner_gui.py"
    
    # Opsi PyInstaller
    options = [
        '--name=WiFi_Scanner_Zidan',
        '--onefile',  # Single file EXE
        '--windowed',  # Tanpa console window
        '--icon=NONE',  # Tidak ada icon (bisa ditambahkan nanti)
        '--distpath=dist',  # Output ke dist folder
        '--workpath=build',  # Temp folder
        '--specpath=.',
        '--clean',  # Bersihkan cache
        '--noconfirm',  # Tidak konfirmasi overwrite
        # Hidden imports untuk modul lokal
        '--hidden-import=config',
        '--hidden-import=ui_components',
        '--hidden-import=network_utils',
        # Path untuk mencari modul
        '--paths=src',
        # '--add-data=images;images',  # Jika ada folder images
    ]
    
    # Perintah lengkap
    # Perintah lengkap menggunakan python -m PyInstaller
    cmd = [sys.executable, '-m', 'PyInstaller'] + options + [main_script]
    
    print("📦 Opsi build yang digunakan:")
    for opt in options:
        print(f"   {opt}")
    print()
    
    # Jalankan PyInstaller
    try:
        print("🔨 Menjalankan PyInstaller...")
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print("✅ Build berhasil!")
        
        # Tampilkan output
        if result.stdout:
            print("Output PyInstaller:")
            print(result.stdout[:500])  # Tampilkan 500 karakter pertama
        
    except subprocess.CalledProcessError as e:
        print("❌ Build gagal!")
        print(f"Error: {e.stderr}")
        return False
    
    return True

def verify_exe():
    """Verifikasi file EXE dibuat"""
    exe_path = r"dist\WiFi_Scanner_Zidan.exe"
    
    if os.path.exists(exe_path):
        size = os.path.getsize(exe_path) / (1024*1024)  # MB
        print(f"\n✅ EXE berhasil dibuat!")
        print(f"📍 Lokasi: {exe_path}")
        print(f"📁 Ukuran: {size:.2f} MB")
        
        # Cek dependencies
        print("\n📋 Dependencies yang termasuk:")
        print("   - Python Runtime")
        print("   - Tkinter GUI Library")
        print("   - Subprocess Module")
        print("   - Threading Module")
        print("   - Platform Module")
        
        return True
    else:
        print(f"\n❌ File EXE tidak ditemukan di: {exe_path}")
        return False

def create_launcher_bat():
    """Buat file .bat untuk memudahkan running"""
    bat_content = """@echo off
echo ========================================
echo     WiFi Scanner Python - EXE Launcher
echo ========================================
echo.
echo Menjalankan WiFi Scanner...
echo.

REM Jalankan sebagai Administrator jika perlu
REM netsh requires admin privileges for WiFi scanning
:checkPrivileges
NET FILE 1>NUL 2>NUL
if '%errorlevel%' == '0' ( goto gotPrivileges ) else ( goto getPrivileges )

:getPrivileges
echo Meminta hak akses Administrator...
echo.
powershell -Command "Start-Process '%~dp0WiFi_Scanner_Zidan.exe' -Verb RunAs"
goto:eof

:gotPrivileges
echo Hak akses Administrator sudah ada.
echo.
start "" "%~dp0WiFi_Scanner_Zidan.exe"
"""
    
    bat_path = r"dist\Run_WiFi_Scanner.bat"
    with open(bat_path, 'w') as f:
        f.write(bat_content)
    
    print(f"📜 File launcher .bat dibuat: {bat_path}")

def main():
    """Fungsi utama"""
    print("\n" + "="*50)
    print("   PEMBUATAN EXE - WiFi Scanner Python")
    print("="*50)
    print("Pembuat: Zidan Ardiansyah")
    print("Mata Kuliah: Network Programming")
    print("="*50)
    
    # Step 1: Bersihkan folder lama
    print("\n📦 Langkah 1: Membersihkan folder build sebelumnya...")
    clean_build_folders()
    
    # Step 2: Build EXE
    print("\n🔨 Langkah 2: Membangun file EXE...")
    if not build_exe():
        print("❌ Gagal membangun EXE. Periksa error di atas.")
        input("Tekan Enter untuk keluar...")
        return
    
    # Step 3: Verifikasi
    print("\n✅ Langkah 3: Verifikasi file EXE...")
    if not verify_exe():
        print("❌ Verifikasi gagal.")
        input("Tekan Enter untuk keluar...")
        return
    
    # Step 4: Buat launcher
    print("\n🚀 Langkah 4: Membuat file launcher...")
    create_launcher_bat()
    
    # Step 5: Instruksi
    print("\n" + "="*50)
    print("🎉 PEMBUATAN EXE SELESAI!")
    print("="*50)
    print("\n📋 INSTRUKSI PENGGUNAAN:")
    print("1. Buka folder: dist")
    print("2. Jalankan file: WiFi_Scanner_Zidan.exe")
    print("   ATAU")
    print("3. Jalankan file: Run_WiFi_Scanner.bat (akan request admin)")
    print("\n⚠️  CATATAN:")
    print("   - Untuk scanning WiFi, jalankan sebagai Administrator")
    print("   - File EXE bisa dipindahkan ke komputer lain (Windows)")
    print("   - Tidak perlu install Python di komputer target")
    print("="*50)
    
    # Buka folder dist
    dist_path = os.path.join(os.getcwd(), "dist")
    print(f"\n📂 Membuka folder: {dist_path}")
    
    # Tanya apakah ingin membuka folder
    response = input("\nBuka folder dist sekarang? (y/n): ").lower()
    if response == 'y':
        os.startfile(dist_path)
    
    input("\nTekan Enter untuk keluar...")

if __name__ == "__main__":
    main()
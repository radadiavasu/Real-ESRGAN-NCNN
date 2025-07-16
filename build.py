# build.py - Build script for creating executable
import sys
import os
import shutil
import subprocess
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app_ncnn.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('bin/*', 'bin'),
        ('models/*', 'models'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'PIL._tkinter_finder',
        'PIL.ImageTk',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'numpy',
        'qdarkstyle',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RealESRGAN-NCNN',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RealESRGAN-NCNN',
)
"""
    
    with open('app_ncnn.spec', 'w', encoding="utf-8") as f:
        f.write(spec_content)

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    subprocess.run([sys.executable, "-m", "PyInstaller", "app_ncnn.spec", "--clean"])

def create_distribution():
    """Create final distribution folder"""
    print("Creating distribution...")
    
    dist_dir = Path("dist_final")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir()
    
    exe_dir = Path("dist/RealESRGAN-NCNN")
    if exe_dir.exists():
        shutil.copytree(exe_dir, dist_dir / "RealESRGAN-NCNN")
    
    readme_content = """
# Real-ESRGAN NCNN Image Upscaler

## Quick Start
1. Extract this ZIP file to any folder
2. Download Real-ESRGAN NCNN models and place them in the 'models' folder
3. Download Real-ESRGAN NCNN executable and place it in the 'bin' folder
4. Double-click 'RealESRGAN-NCNN.exe' to run the application

## Required Files Structure:
```
RealESRGAN-NCNN/
├── RealESRGAN-NCNN.exe          # Main application
├── bin/
│   └── realesrgan-ncnn-vulkan.exe   # NCNN executable
├── models/
│   ├── realesrgan-x4plus.param
│   ├── realesrgan-x4plus.bin
│   ├── realesrgan-x4plus-anime.param
│   ├── realesrgan-x4plus-anime.bin
│   └── ...
└── _internal/                   # Application dependencies (auto-generated)
```

## Download Links:
- NCNN Executable: https://github.com/xinntao/Real-ESRGAN/releases
- Models: https://github.com/xinntao/Real-ESRGAN/releases

## Usage:
1. Click 'Load Image' to select an image
2. Choose model and scale settings
3. Click 'Process Image' to upscale
4. Click 'Save Result' to save the upscaled image

## Supported Formats:
- Input: PNG, JPG, JPEG, BMP, TIF, TIFF, WEBP
- Output: JPG, PNG, WEBP

## System Requirements:
- Windows 10/11 (64-bit)
- Vulkan-compatible GPU (recommended)
- 4GB+ RAM
- 1GB+ free disk space

## Troubleshooting:
- If the app doesn't start, ensure all files are extracted properly
- If processing fails, check that the NCNN executable is in the 'bin' folder
- For GPU acceleration, ensure Vulkan drivers are installed
"""

    with open(dist_dir / "README.txt", 'w', encoding="utf-8") as f:
        f.write(readme_content)
    
    (dist_dir / "RealESRGAN-NCNN" / "bin").mkdir(parents=True, exist_ok=True)
    (dist_dir / "RealESRGAN-NCNN" / "models").mkdir(parents=True, exist_ok=True)
    
    # Create batch file for easy execution
    batch_content = """@echo off
cd /d "%~dp0"
start "" "RealESRGAN-NCNN.exe"
"""
    
    with open(dist_dir / "RealESRGAN-NCNN" / "Run_RealESRGAN.bat", 'w', encoding="utf-8") as f:
        f.write(batch_content)
    
    print(f"Distribution created in: {dist_dir}")
    print("Next steps:")
    print("1. Download Real-ESRGAN NCNN executable to bin/ folder")
    print("2. Download model files to models/ folder")
    print("3. Create ZIP file for distribution")

def main():
    print("Real-ESRGAN NCNN Build Script")
    print("=" * 40)
    
    if not os.path.exists('app_ncnn.py'):
        print("Error: app_ncnn.py not found!")
        print("Please ensure the main application file is in the current directory.")
        return
    
    try:
        install_dependencies()
        
        create_spec_file()
        
        build_executable()
        
        create_distribution()
        
        print("\n" + "=" * 40)
        print("Build completed successfully!")
        print("Check the 'dist_final' folder for the final distribution.")
        
    except Exception as e:
        print(f"Build failed: {e}")
        return

if __name__ == "__main__":
    main()

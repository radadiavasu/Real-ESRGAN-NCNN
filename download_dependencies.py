# download_dependencies.py - Script to download NCNN executable and models
import os
import requests
import zipfile
import shutil
from pathlib import Path
import json

def download_file(url, filename):
    """Download a file with progress indication"""
    print(f"Downloading {filename}...")
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    progress = (downloaded / total_size) * 100
                    print(f"\rProgress: {progress:.1f}%", end='', flush=True)
    
    print(f"\nDownloaded: {filename}")

def extract_zip(zip_path, extract_to):
    """Extract ZIP file"""
    print(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Extracted to: {extract_to}")

def setup_ncnn_executable():
    """Download and setup NCNN executable"""
    print("Setting up NCNN executable...")
    
    # Create bin directory
    bin_dir = Path("bin")
    bin_dir.mkdir(exist_ok=True)
    
    # Download URLs (you'll need to update these with actual release URLs)
    ncnn_urls = {
        "windows": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-windows.zip",
        # "linux": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip",
        # "macos": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/realesrgan-ncnn-vulkan-20220424-macos.zip"
    }
    
    # Detect platform
    import platform
    system = platform.system().lower()
    
    if system == "windows":
        download_url = ncnn_urls["windows"]
        executable_name = "realesrgan-ncnn-vulkan.exe"
    elif system == "linux":
        download_url = ncnn_urls["linux"]
        executable_name = "realesrgan-ncnn-vulkan"
    elif system == "darwin":
        download_url = ncnn_urls["macos"]
        executable_name = "realesrgan-ncnn-vulkan"
    else:
        print(f"Unsupported platform: {system}")
        return False
    
    # Download NCNN package
    zip_filename = f"ncnn-{system}.zip"
    
    try:
        download_file(download_url, zip_filename)
        
        # Extract
        extract_zip(zip_filename, "temp_ncnn")
        
        # Find and copy executable
        for root, dirs, files in os.walk("temp_ncnn"):
            for file in files:
                if file == executable_name:
                    src = os.path.join(root, file)
                    dst = bin_dir / file
                    shutil.copy2(src, dst)
                    print(f"Copied executable: {dst}")
                    
                    # Make executable on Unix systems
                    if system != "windows":
                        os.chmod(dst, 0o755)
                    
                    break
        
        # Cleanup
        os.remove(zip_filename)
        shutil.rmtree("temp_ncnn", ignore_errors=True)
        
        return True
        
    except Exception as e:
        print(f"Error downloading NCNN executable: {e}")
        return False

def setup_models():
    """Download and setup model files"""
    print("Setting up model files...")
    
    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Model download URLs
    models = {
        "realesrgan-x4plus": {
            "param": "G:\realesrgen-app\realesrgan-ncnn-vulkan-20220424-windows\models\realesrgan-x4plus.param",
            "bin": "G:\realesrgen-app\realesrgan-ncnn-vulkan-20220424-windows\models\realesrgan-x4plus.bin"
        },
        "realesrgan-x4plus-anime": {
            "param": "G:\realesrgen-app\realesrgan-ncnn-vulkan-20220424-windows\models\realesrgan-x4plus-anime.param",
            "bin": "G:\realesrgen-app\realesrgan-ncnn-vulkan-20220424-windows\models\realesrgan-x4plus-anime.bin"
        },
        # "realesrnet-x4plus": {
        #     "param": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/realesrnet-x4plus.param",
        #     "bin": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/realesrnet-x4plus.bin"
        # }
    }
    
    success = True
    for model_name, urls in models.items():
        try:
            # Download param file
            param_file = models_dir / f"{model_name}.param"
            download_file(urls["param"], param_file)
            
            # Download bin file
            bin_file = models_dir / f"{model_name}.bin"
            download_file(urls["bin"], bin_file)
            
        except Exception as e:
            print(f"Error downloading {model_name}: {e}")
            success = False
    
    return success

def create_config_file():
    """Create configuration file"""
    config = {
        "version": "1.0",
        "models": {
            "realesrgan-x4plus": {
                "param": "models/realesrgan-x4plus.param",
                "bin": "models/realesrgan-x4plus.bin",
                "scale": 4
            },
            "realesrgan-x4plus-anime": {
                "param": "models/realesrgan-x4plus-anime.param",
                "bin": "models/realesrgan-x4plus-anime.bin",
                "scale": 4
            },
            # "realesrnet-x4plus": {
            #     "param": "models/realesrnet-x4plus.param",
            #     "bin": "models/realesrnet-x4plus.bin",
            #     "scale": 4
            # }
        },
        "executable": {
            "windows": "bin/realesrgan-ncnn-vulkan.exe",
            "linux": "bin/realesrgan-ncnn-vulkan",
            "macos": "bin/realesrgan-ncnn-vulkan"
        }
    }
    
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("Created config.json")

def main():
    print("Real-ESRGAN NCNN Dependencies Setup")
    print("=" * 40)
    
    try:
        # Setup NCNN executable
        if setup_ncnn_executable():
            print("✓ NCNN executable setup completed")
        else:
            print("✗ NCNN executable setup failed")
        
        # Setup models
        if setup_models():
            print("✓ Models setup completed")
        else:
            print("✗ Models setup failed")
        
        # Create config file
        create_config_file()
        
        print("\n" + "=" * 40)
        print("Dependencies setup completed!")
        print("You can now run the build script to create the executable.")
        
    except Exception as e:
        print(f"Setup failed: {e}")

if __name__ == "__main__":
    main()
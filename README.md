# Real-ESRGAN NCNN Image Upscaler

## 🔧Quick Start (For going through the code.)
1. Extract this ZIP file to any folder
2. Download Real-ESRGAN NCNN models and place them in the `models` folder
3. Download Real-ESRGAN NCNN executable and place it in the `bin` folder
4. If you don't want to download manually then run `download_dependencies.py` file directly.
5. Run `build.py` file for generate `RealESRGAN-NCNN.exe`.
6. you have to replace `dist_final` models and bin to `download_dependencies.py` models and bin.
7. Double-click `RealESRGAN-NCNN.exe` to run the application

## 👀Required Files Structure:
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

## ⚡Usage:
1. Click `Load Image` to select an image
2. Choose model and scale settings
3. Click `Process Image` to upscale
4. Click `Save Result` to save the upscaled image

## Supported Formats:
- Input: PNG, JPG, JPEG, BMP, TIF, TIFF, WEBP
- Output: JPG, PNG, WEBP

## 💻System Performance:
|Windows|Processor|RAM|GPU|Toal Time(s)|Perfomance|
|---|---|---|---|---|---|
|10|I3-I5|4/4+|Default|1500-2100|Too Slow|
|10|I7|8+|Default|600|Slow|
|10|I7|8+|GTX or AMD GPU|300|Quite Good|
|11|I3-I5|8+|Default|1300-1500|Too Slow|
|11|I7|8+|Default|900-1100|Slow|
|11|I7|8+|GTX or AMD GPU|300|Good|
|11|I7|16+|RTX or AMD GPU|15-30|Execellent|

# Suggestion
- Windows 11 (64-bit)
- Processor I5 12th gen beat I7 otherwise I7 latest
- Compatible GPU: RTX or amd rx best if have GTX then its fine
- RAM: 8GB+ RAM
- 1GB+ free disk space (For storing output images)

## 🚧Troubleshooting:
- If the app doesn't start, ensure all files are extracted properly
- If processing fails, check that the NCNN executable is in the 'bin' folder
- For GPU acceleration, ensure compatible drivers are installed

## 💪Performance over CPU / GPU
- CPU: Takes around 15-20 min for per image.
- GPU: Depend on GPU in my case I have NVIDIA RTX 4060 takes around 20-30 sec per img.

## 📝Note
- Always set `Scale settings` on 4x. if set in 2x raise error because model param's can only compute for 4x.
- Always prefer less than 2k image dimentions, check h * w before processing otherwise error occur for exceeding the image pixels. You can initally decrease their pixels because after processing you get 4k level image.

## 🚩Updated Build Releases
- Consider latest releases at https://github.com/radadiavasu/Real-ESRGAN-NCNN/releases/ section.

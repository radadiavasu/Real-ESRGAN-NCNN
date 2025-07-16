import sys
import os
import subprocess
import numpy as np
from PIL import Image
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                             QFileDialog, QHBoxLayout, QVBoxLayout, 
                             QWidget, QFrame, QSplitter, QProgressBar, QComboBox,
                             QSpinBox, QCheckBox, QGridLayout, QGroupBox, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QPixmap, QImage, QFont
import tempfile
import shutil
import json

try:
    import qdarkstyle
    has_qdarkstyle = True
except ImportError:
    has_qdarkstyle = False

class NCNNUpscalerThread(QThread):
    progress = Signal(int)
    result = Signal(str)  # output image
    finished = Signal()
    error = Signal(str)
    
    def __init__(self, realesrgan_ncnn_path, input_path, output_path, scale=4, model_name="realesrgan-x4plus"):
        super().__init__()
        self.realesrgan_ncnn_path = realesrgan_ncnn_path
        self.input_path = input_path
        self.output_path = output_path
        self.scale = scale
        self.model_name = model_name
        
    def run(self):
        try:
            self.progress.emit(10)
            
            # Prepare command
            cmd = [
                self.realesrgan_ncnn_path,
                "-i", self.input_path,
                "-o", self.output_path,
                "-n", self.model_name,
                "-s", str(self.scale),
                "-f", "jpg"  # Output format
            ]
            
            self.progress.emit(30)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.progress.emit(90)
                self.result.emit(self.output_path)
                self.progress.emit(100)
                self.finished.emit()
            else:
                self.error.emit(f"NCNN process failed: {result.stderr}")
                
        except Exception as e:
            self.error.emit(str(e))

class RealESRGANNCNNApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.input_image_path = None
        self.input_image = None
        self.output_image = None
        self.output_image_path = None
        self.temp_dir = tempfile.mkdtemp()
        
        self.realesrgan_ncnn_path = self.find_ncnn_executable()
        
        self.setWindowTitle("Real-ESRGAN NCNN Image Upscaler")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()
        
        self.check_ncnn_availability()

    def find_ncnn_executable(self):
        """Find the Real-ESRGAN NCNN executable"""
        possible_names = [
            "realesrgan-ncnn-vulkan.exe",
            "realesrgan-ncnn-vulkan",
            "realesrgan-ncnn.exe",
            "realesrgan-ncnn"
        ]
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        search_paths = [
            current_dir,
            os.path.join(current_dir, "bin"),
            os.path.join(current_dir, "ncnn"),
            os.path.join(current_dir, "realesrgan-ncnn"),
            os.path.join(current_dir, "realesrgan-ncnn-vulkan")
        ]
        
        for path in search_paths:
            for name in possible_names:
                full_path = os.path.join(path, name)
                if os.path.exists(full_path):
                    return full_path
        
        return None

    def check_ncnn_availability(self):
        """Check if NCNN executable is available"""
        if not self.realesrgan_ncnn_path:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText("NCNN Executable Not Found")
            msg.setInformativeText("Real-ESRGAN NCNN executable not found. Please ensure it's in the same directory as this application.")
            msg.setWindowTitle("Error")
            msg.exec()
            self.statusBar().showMessage("NCNN executable not found")
            return False
        
        try:
            result = subprocess.run([self.realesrgan_ncnn_path, "-h"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 or "Usage:" in result.stdout or "Usage:" in result.stderr:
                self.statusBar().showMessage("NCNN executable found and ready")
                return True
        except:
            pass
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText("NCNN Executable Issue")
        msg.setInformativeText("Found NCNN executable but it may not be working correctly. Please check your installation.")
        msg.setWindowTitle("Warning")
        msg.exec()
        return False

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        header_layout = QHBoxLayout()
        logo_label = QLabel("Real-ESRGAN NCNN Image Upscaler")
        logo_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(logo_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Image area (side by side)
        image_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Input image frame
        input_frame = QFrame()
        input_frame.setFrameShape(QFrame.Shape.StyledPanel)
        input_layout = QVBoxLayout(input_frame)
        
        input_label = QLabel("Input Image")
        input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        input_label.setFont(QFont("Arial", 12))
        
        self.input_image_view = QLabel()
        self.input_image_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_image_view.setMinimumSize(400, 400)
        self.input_image_view.setStyleSheet("background-color: #2a2a2a; border: 1px solid #555;")
        self.input_image_view.setText("No image selected")
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_image_view)
        
        # Output image frame
        output_frame = QFrame()
        output_frame.setFrameShape(QFrame.Shape.StyledPanel)
        output_layout = QVBoxLayout(output_frame)
        
        output_label = QLabel("Output Image")
        output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        output_label.setFont(QFont("Arial", 12))
        
        self.output_image_view = QLabel()
        self.output_image_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.output_image_view.setMinimumSize(400, 400)
        self.output_image_view.setStyleSheet("background-color: #2a2a2a; border: 1px solid #555;")
        self.output_image_view.setText("No output yet")
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_image_view)
        
        # frames to splitter
        image_splitter.addWidget(input_frame)
        image_splitter.addWidget(output_frame)
        
        # Controls section
        controls_frame = QFrame()
        controls_frame.setFrameShape(QFrame.Shape.StyledPanel)
        controls_layout = QGridLayout(controls_frame)
        
        # Group box for input controls
        input_group = QGroupBox("Input Controls")
        input_controls = QVBoxLayout(input_group)
        
        self.load_btn = QPushButton("Load Image")
        self.load_btn.clicked.connect(self.load_image)
        input_controls.addWidget(self.load_btn)
        
        controls_layout.addWidget(input_group, 0, 0)
        
        model_group = QGroupBox("Model Settings")
        model_controls = QGridLayout(model_group)
        
        model_controls.addWidget(QLabel("Model:"), 0, 0)
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "realesrgan-x4plus", 
            "realesrgan-x4plus-anime", 
            "realesrnet-x4plus"
        ])
        model_controls.addWidget(self.model_combo, 0, 1)
        
        model_controls.addWidget(QLabel("Scale:"), 1, 0)
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["2", "4"])
        self.scale_combo.setCurrentIndex(1)  # Default to 4
        model_controls.addWidget(self.scale_combo, 1, 1)
        
        model_controls.addWidget(QLabel("Output Format:"), 2, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["jpg", "png", "webp"])
        model_controls.addWidget(self.format_combo, 2, 1)
        
        controls_layout.addWidget(model_group, 0, 1, 2, 1)
        
        output_group = QGroupBox("Output Controls")
        output_controls = QVBoxLayout(output_group)
        
        self.process_btn = QPushButton("Process Image")
        self.process_btn.clicked.connect(self.process_image)
        self.process_btn.setEnabled(False)
        output_controls.addWidget(self.process_btn)
        
        self.save_btn = QPushButton("Save Result")
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setEnabled(False)
        output_controls.addWidget(self.save_btn)
        
        controls_layout.addWidget(output_group, 1, 0)
        
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.status_label)
        
        controls_layout.addWidget(progress_group, 2, 0, 1, 2)
        
        # Add all components to main layout
        main_layout.addWidget(image_splitter, 3)
        main_layout.addWidget(controls_frame)
        
        # Set central widget
        self.setCentralWidget(main_widget)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp)"
        )
        
        if file_path:
            try:
                self.input_image_path = file_path
                self.input_image = Image.open(file_path).convert('RGB')
                
                self.display_image(self.input_image, self.input_image_view)
                
                self.process_btn.setEnabled(True)
                
                width, height = self.input_image.size
                self.statusBar().showMessage(f"Loaded image: {os.path.basename(file_path)} ({width}x{height})")
                self.status_label.setText(f"Image loaded: {width}x{height}")
            
            except Exception as e:
                self.statusBar().showMessage(f"Error loading image: {str(e)}")
                
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText("Image Load Error")
                msg.setInformativeText(f"Failed to load image: {str(e)}")
                msg.setWindowTitle("Error")
                msg.exec()
    
    def display_image(self, img, label):
        if isinstance(img, str):
            # If it's a path, load the image
            img = Image.open(img).convert('RGB')
        elif isinstance(img, np.ndarray):
            # Convert numpy array to PIL Image
            img = Image.fromarray(img)
        
        # Get label dimensions
        label_width = label.width()
        label_height = label.height()
        
        # If label dimensions are 0 (not yet rendered), use minimum size
        if label_width <= 100:
            label_width = label.minimumWidth()
        if label_height <= 100:
            label_height = label.minimumHeight()
        
        # Convert PIL Image to QImage
        img_qt = img.convert("RGBA")
        data = img_qt.tobytes("raw", "RGBA")
        qim = QImage(data, img.width, img.height, QImage.Format.Format_RGBA8888)
        
        # Scale image to fit label while maintaining aspect ratio
        pixmap = QPixmap.fromImage(qim)
        pixmap = pixmap.scaled(label_width, label_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        # Set pixmap to label
        label.setPixmap(pixmap)
    
    def process_image(self):
        if self.input_image_path is None or self.realesrgan_ncnn_path is None:
            return
        
        self.process_btn.setEnabled(False)
        self.load_btn.setEnabled(False)
        
        self.progress_bar.setValue(0)
        self.status_label.setText("Processing...")
        
        # Get settings
        model_name = self.model_combo.currentText()
        scale = int(self.scale_combo.currentText())
        output_format = self.format_combo.currentText()
        
        input_basename = os.path.basename(self.input_image_path)
        name, _ = os.path.splitext(input_basename)
        self.output_image_path = os.path.join(self.temp_dir, f"{name}_upscaled.{output_format}")
        
        # Create thread for processing
        self.upscaler_thread = NCNNUpscalerThread(
            self.realesrgan_ncnn_path, 
            self.input_image_path, 
            self.output_image_path, 
            scale, 
            model_name
        )
        self.upscaler_thread.progress.connect(self.update_progress)
        self.upscaler_thread.result.connect(self.handle_result)
        self.upscaler_thread.finished.connect(self.processing_finished)
        self.upscaler_thread.error.connect(self.handle_error)
        
        # Start processing
        self.statusBar().showMessage("Processing image...")
        self.upscaler_thread.start()
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.status_label.setText(f"Processing... {value}%")
    
    def handle_result(self, output_path):
        try:
            # Load and display output image
            self.output_image = Image.open(output_path).convert('RGB')
            self.display_image(self.output_image, self.output_image_view)
            
            # Enable save button
            self.save_btn.setEnabled(True)
            
            # Update status with image dimensions
            width, height = self.output_image.size
            self.statusBar().showMessage(f"Processing complete! Output size: {width}x{height}")
            self.status_label.setText(f"Complete! Output: {width}x{height}")
            
        except Exception as e:
            self.handle_error(f"Error loading result: {str(e)}")
    
    def processing_finished(self):
        self.process_btn.setEnabled(True)
        self.load_btn.setEnabled(True)
    
    def handle_error(self, error_msg):
        self.process_btn.setEnabled(True)
        self.load_btn.setEnabled(True)
        
        self.statusBar().showMessage(f"Error: {error_msg}")
        self.status_label.setText("Error occurred")
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText("Processing Error")
        msg.setInformativeText(f"Error during processing: {error_msg}")
        msg.setWindowTitle("Error")
        msg.exec()
    
    def save_image(self):
        if self.output_image is None:
            return
        
        # Get default filename
        input_basename = os.path.basename(self.input_image_path)
        name, ext = os.path.splitext(input_basename)
        output_format = self.format_combo.currentText()
        default_name = f"{name}_upscaled.{output_format}"
        
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", default_name, f"Image Files (*.{output_format})"
        )
        
        if save_path:
            try:
                # Copy the processed image to the selected location
                if os.path.exists(self.output_image_path):
                    shutil.copy2(self.output_image_path, save_path)
                else:
                    # Fallback: save using PIL
                    self.output_image.save(save_path)
                
                self.statusBar().showMessage(f"Saved image as: {os.path.basename(save_path)}")
                self.status_label.setText("Image saved successfully")
            
            except Exception as e:
                self.statusBar().showMessage(f"Error saving image: {str(e)}")
                
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText("Save Error")
                msg.setInformativeText(f"Failed to save image: {str(e)}")
                msg.setWindowTitle("Error")
                msg.exec()
    
    def closeEvent(self, event):
        """Clean up temporary directory"""
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    app.setApplicationName("Real-ESRGAN NCNN")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Real-ESRGAN")
    
    # Apply dark theme if qdarkstyle is available
    if has_qdarkstyle:
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))
    else:
        app.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2D2D30;
                color: #F1F1F1;
            }
            QPushButton {
                background-color: #3F3F46;
                color: #F1F1F1;
                border: 1px solid #555555;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #2D2D30;
            }
            QPushButton:disabled {
                background-color: #1E1E1E;
                color: #888888;
            }
            QLabel {
                color: #F1F1F1;
            }
            QProgressBar {
                text-align: center;
                color: #F1F1F1;
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #3F3F46;
            }
            QProgressBar::chunk {
                background-color: #007ACC;
                border-radius: 3px;
            }
            QComboBox {
                background-color: #3F3F46;
                color: #F1F1F1;
                border: 1px solid #555555;
                padding: 4px;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #F1F1F1;
                margin-right: 6px;
            }
            QSpinBox {
                background-color: #3F3F46;
                color: #F1F1F1;
                border: 1px solid #555555;
                padding: 4px;
                border-radius: 3px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QFrame {
                border: 1px solid #555555;
                border-radius: 4px;
            }
        """)
    
    window = RealESRGANNCNNApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

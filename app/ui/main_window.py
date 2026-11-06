"""Main application window for Frayed Text PNG Generator."""
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QFileDialog, QMessageBox, QStatusBar
)
from PySide6.QtCore import QTimer, QThread, Signal, Slot
from app.ui.controls_panel import ControlsPanel
from app.ui.preview_widget import PreviewWidget
from app.core.engine import FrayedTextEngine
from app.models.render_config import RenderConfig

class RenderWorker(QThread):
    """Background worker to render preview image without freezing the UI."""
    rendered = Signal(object) # PIL Image
    error = Signal(str)

    def __init__(self, config: RenderConfig, parent=None):
        super().__init__(parent)
        self.config = config

    def run(self):
        try:
            # 1x scale for fast real-time preview
            engine = FrayedTextEngine(supersampling=self.config.output.supersampling)
            img = engine.render(self.config)
            self.rendered.emit(img)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Frayed Text PNG Generator — v1.0")
        self.resize(1200, 750)

        # Main layout
        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.controls = ControlsPanel()
        self.preview = PreviewWidget()

        layout.addWidget(self.controls, 0)
        layout.addWidget(self.preview, 1)

        self.setCentralWidget(central)
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Debounce timer for smooth slider dragging
        self.debounce_timer = QTimer(self)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(150)
        self.debounce_timer.timeout.connect(self._start_preview_render)

        self.active_worker = None

        # Connections
        self.controls.configChanged.connect(self._on_config_changed)
        self.controls.exportRequested.connect(self._on_export_requested)

        # Trigger initial preview
        QTimer.singleShot(100, self._start_preview_render)

    def _on_config_changed(self):
        self.status.showMessage("Updating preview...")
        self.debounce_timer.start()

    def _start_preview_render(self):
        # If a worker is already running, wait or cancel
        if self.active_worker and self.active_worker.isRunning():
            self.debounce_timer.start(50)
            return

        config = self.controls.get_render_config(supersampling=1)
        self.active_worker = RenderWorker(config, self)
        self.active_worker.rendered.connect(self._on_render_finished)
        self.active_worker.error.connect(self._on_render_error)
        self.active_worker.start()

    @Slot(object)
    def _on_render_finished(self, pil_image):
        self.preview.set_pil_image(pil_image)
        self.status.showMessage(f"Preview Ready ({pil_image.width}x{pil_image.height} px)", 3000)

    @Slot(str)
    def _on_render_error(self, err_msg):
        self.status.showMessage(f"Render Error: {err_msg}", 5000)

    def _on_export_requested(self):
        config = self.controls.get_render_config(supersampling=2) # 2x supersampling for high-quality export
        sub_suffix = f"_{config.subtext.get_effective_text().strip().replace(' ', '_')}" if config.subtext.enabled else ""
        default_name = f"{config.text.get_effective_text().strip().replace(' ', '_')}{sub_suffix}_frayed.png"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Transparent PNG", default_name, "PNG Files (*.png)"
        )
        if not file_path:
            return

        if not file_path.lower().endswith(".png"):
            file_path += ".png"

        try:
            self.status.showMessage("Exporting high-resolution PNG...")
            engine = FrayedTextEngine(supersampling=2)
            high_res_img = engine.render(config)
            high_res_img.save(file_path, "PNG")
            self.status.showMessage(f"Exported: {file_path}", 5000)
            QMessageBox.information(
                self, "Export Successful",
                f"Transparent PNG saved successfully to:\n\n{file_path}\n\nDimensions: {high_res_img.width}x{high_res_img.height} px"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export image:\n{str(e)}")

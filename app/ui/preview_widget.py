"""Canvas preview widget with transparency checkerboard background."""
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QBrush, QPixmap, QImage
from PySide6.QtCore import Qt, QRectF
from PIL import Image

class PreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap: QPixmap = None
        self.setMinimumSize(400, 300)
        self.check_size = 16
        self.color1 = QColor(245, 245, 245)
        self.color2 = QColor(215, 215, 215)

    def set_pil_image(self, pil_image: Image.Image):
        """Converts RGBA PIL Image to QPixmap and triggers repaint."""
        if pil_image is None:
            self.pixmap = None
            self.update()
            return

        if pil_image.mode != "RGBA":
            pil_image = pil_image.convert("RGBA")

        data = pil_image.tobytes("raw", "RGBA")
        qim = QImage(data, pil_image.width, pil_image.height, QImage.Format_RGBA8888)
        self.pixmap = QPixmap.fromImage(qim)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # 1. Draw Checkerboard background
        w = self.width()
        h = self.height()
        c_size = self.check_size

        for y in range(0, h, c_size):
            for x in range(0, w, c_size):
                if ((x // c_size) + (y // c_size)) % 2 == 0:
                    painter.fillRect(x, y, c_size, c_size, self.color1)
                else:
                    painter.fillRect(x, y, c_size, c_size, self.color2)

        # 2. Draw Pixmap centered and scaled
        if self.pixmap and not self.pixmap.isNull():
            pm_w = self.pixmap.width()
            pm_h = self.pixmap.height()

            # Keep aspect ratio with some margin
            margin = 30
            avail_w = max(10, w - margin * 2)
            avail_h = max(10, h - margin * 2)

            scale_w = avail_w / pm_w
            scale_h = avail_h / pm_h
            scale = min(scale_w, scale_h, 1.2) # Max zoom 1.2x if small, otherwise fit

            target_w = int(pm_w * scale)
            target_h = int(pm_h * scale)
            target_x = (w - target_w) // 2
            target_y = (h - target_h) // 2

            dest_rect = QRectF(target_x, target_y, target_w, target_h)
            painter.drawPixmap(dest_rect.toRect(), self.pixmap)

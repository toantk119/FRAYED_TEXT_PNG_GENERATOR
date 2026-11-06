# PROJECT STATE — FRAYED TEXT PNG GENERATOR
<!-- Standards: Unified Delivery Governance v3.7 -->

## 1. Trạng Thái Hiện Tại
- **Phiên bản**: v1.2 (Photoshop-style Font Picker & 2600+ Font Family Tree)
- **Tình trạng kiểm thử**: 22/22 Unit tests PASS 100% (`init.ps1`).
- **Môi trường hoạt động**: `C:\JerseyShift\.venv` (Python 3.12+, PySide6, OpenCV, NumPy, Pillow).
- **Điểm khởi chạy**: 
  - GUI: `C:\FRAYED_TEXT_PNG_GENERATOR\run_app.bat` hoặc `python main.py`
  - CLI: `python run_cli.py --text "Eintracht" --subtext "FRANKFURT" --subtext-align "right" ...`

## 2. Kiến Trúc Hoàn Thành
- `app/models/render_config.py`: Data models tham số hóa toàn diện 5 bảng màu & hiệu ứng, `SubTextConfig` (tỉ lệ, alignment, offset X/Y, màu riêng).
- `app/core/font_manager.py`: Bộ quét Font Windows Registry siêu tốc (2,600+ fonts trong ~0.1s), gom nhóm Family $\rightarrow$ Style chuẩn PSD, quản lý Favorites ⭐ và Recent fonts.
- `app/core/text_renderer.py`: Typography & trích xuất 8-bit Alpha Mask 2 tầng (Dual-tier) thống nhất hình học.
- `app/core/stroke_engine.py`: Giãn nở viền trong (Inner) và viền ngoài (Outer) bao trọn khối 2 tầng.
- `app/core/dash_engine.py`: Đường chỉ may nét đứt đều đặn (Arc-length) bao quát chu vi khối hợp nhất.
- `app/core/fray_engine.py`: Thuật toán sinh sợi tưa rua đa tầng theo vector pháp tuyến (Normal Field Gradient).
- `app/core/compositor.py`: Hòa trộn đa tầng màu độc lập (cho phép tầng 1 và tầng 2 có màu riêng) & khử răng cưa Lanczos.
- `app/ui/font_picker_dialog.py`: Hộp thoại Bộ chọn Font chuyên nghiệp chuẩn Adobe Photoshop (cây Family $\rightarrow$ Styles, live search filter, preview chữ mẫu trực quan, ⭐ Favorites, 🕒 Recent).
- `app/ui/controls_panel.py`: Tích hợp chọn Font PSD cho cả Tầng 1 và Tầng 2, live preview real-time.

## 3. Session Handoff Checklist
- [x] Lát cắt 1: Core Rendering Engine (CLI) hoàn thành và pass kiểm nghiệm thị giác.
- [x] Lát cắt 2: PySide6 Desktop GUI hoàn thành và đã kiểm thử thành công trên Windows.
- [x] Lát cắt 3: Bổ sung tính năng viết HOA toàn bộ (ALL CAPS) với nút tick chọn trên GUI và cờ `--uppercase` trên CLI.
- [x] Lát cắt 4: Bổ sung tính năng Chữ 2 tầng (Dual-tier Subtext) căn lề Trái/Phải/Giữa, offset X/Y, màu riêng và khối đồ họa thống nhất.
- [x] Lát cắt 5: Xây dựng Hộp thoại Font Picker chuyên sâu chuẩn Photoshop (Family -> Styles, Search, Live Preview, Favorites).
- [x] Nghiệm thu 22/22 Automated Unit Tests PASS 100%.
- [x] Git Commit & Push cập nhật lên GitHub remote.

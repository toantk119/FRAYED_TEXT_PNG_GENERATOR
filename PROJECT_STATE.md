# PROJECT STATE — FRAYED TEXT PNG GENERATOR
<!-- Standards: Unified Delivery Governance v3.7 -->

## 1. Trạng Thái Hiện Tại
- **Phiên bản**: v1.1 (Dual-tier Subtext & Unified Silhouette Architecture)
- **Tình trạng kiểm thử**: 18/18 Unit tests PASS 100% (`init.ps1`).
- **Môi trường hoạt động**: `C:\JerseyShift\.venv` (Python 3.12+, PySide6, OpenCV, NumPy, Pillow).
- **Điểm khởi chạy**: 
  - GUI: `C:\FRAYED_TEXT_PNG_GENERATOR\run_app.bat` hoặc `python main.py`
  - CLI: `python run_cli.py --text "Eintracht" --subtext "FRANKFURT" --subtext-align "right" ...`

## 2. Kiến Trúc Hoàn Thành
- `app/models/render_config.py`: Data models tham số hóa toàn diện 5 bảng màu & hiệu ứng, bổ sung `SubTextConfig` (tỉ lệ scale_ratio, alignment trái/phải/giữa, offset X/Y, màu riêng).
- `app/core/text_renderer.py`: Typography & trích xuất 8-bit Alpha Mask 2 tầng (Dual-tier) thống nhất hình học.
- `app/core/stroke_engine.py`: Giãn nở viền trong (Inner) và viền ngoài (Outer) bao trọn khối 2 tầng.
- `app/core/dash_engine.py`: Đường chỉ may nét đứt đều đặn (Arc-length) bao quát chu vi khối hợp nhất.
- `app/core/fray_engine.py`: Thuật toán sinh sợi tưa rua đa tầng theo vector pháp tuyến (Normal Field Gradient).
- `app/core/compositor.py`: Hòa trộn đa tầng màu độc lập (cho phép tầng 1 và tầng 2 có màu riêng) & khử răng cưa Lanczos.
- `app/ui/`: Giao diện Desktop PySide6 tích hợp nhóm điều khiển "Chữ Tầng 2 (Dual-tier / Sub-text)" tương tác real-time mượt mà.

## 3. Session Handoff Checklist
- [x] Lát cắt 1: Core Rendering Engine (CLI) hoàn thành và pass kiểm nghiệm thị giác.
- [x] Lát cắt 2: PySide6 Desktop GUI hoàn thành và đã kiểm thử thành công trên Windows.
- [x] Lát cắt 3: Bổ sung tính năng viết HOA toàn bộ (ALL CAPS) với nút tick chọn trên GUI và cờ `--uppercase` trên CLI.
- [x] Lát cắt 4: Bổ sung tính năng Chữ 2 tầng (Dual-tier Subtext) căn lề Trái/Phải/Giữa, offset X/Y, màu riêng và khối đồ họa thống nhất.
- [x] Nghiệm thu 18/18 Automated Unit Tests PASS 100%.
- [x] Git Commit & Push cập nhật lên GitHub remote.

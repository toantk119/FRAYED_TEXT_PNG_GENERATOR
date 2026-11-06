# PROJECT STATE — FRAYED TEXT PNG GENERATOR
<!-- Standards: Unified Delivery Governance v3.7 -->

## 1. Trạng Thái Hiện Tại
- **Phiên bản**: v1.1 (Uppercase Feature & Git Integration)
- **Tình trạng kiểm thử**: 14/14 Unit tests PASS 100% (`init.ps1`).
- **Môi trường hoạt động**: `C:\JerseyShift\.venv` (Python 3.12+, PySide6, OpenCV, NumPy, Pillow).
- **Điểm khởi chạy**: 
  - GUI: `C:\FRAYED_TEXT_PNG_GENERATOR\run_app.bat` hoặc `python main.py`
  - CLI: `python run_cli.py --text "Team Name" [--uppercase] ...`

## 2. Kiến Trúc Hoàn Thành
- `app/models/render_config.py`: Data models tham số hóa toàn diện 5 bảng màu & hiệu ứng, bổ sung `uppercase: bool` và `get_effective_text()`.
- `app/core/text_renderer.py`: Typography & trích xuất 8-bit Alpha Mask (hỗ trợ chuyển đổi tự động ALL CAPS).
- `app/core/stroke_engine.py`: Giãn nở viền trong (Inner) và viền ngoài (Outer).
- `app/core/dash_engine.py`: Đường chỉ may nét đứt đều đặn (Arc-length) bao quát cả outer và inner holes.
- `app/core/fray_engine.py`: Thuật toán sinh sợi tưa rua đa tầng theo vector pháp tuyến (Normal Field Gradient).
- `app/core/compositor.py`: Hòa trộn đa tầng màu độc lập & khử răng cưa Lanczos.
- `app/ui/`: Giao diện Desktop PySide6 với Canvas bàn cờ (Checkerboard), nút tick ALL CAPS và luồng phụ RenderWorker không giật lag.

## 3. Session Handoff Checklist
- [x] Lát cắt 1: Core Rendering Engine (CLI) hoàn thành và pass kiểm nghiệm thị giác.
- [x] Lát cắt 2: PySide6 Desktop GUI hoàn thành và đã kiểm thử thành công trên Windows.
- [x] Lát cắt 3: Bổ sung tính năng viết HOA toàn bộ (ALL CAPS) với nút tick chọn trên GUI và cờ `--uppercase` trên CLI.
- [x] Đã khởi tạo Git repository và push lên remote https://github.com/toantk119/FRAYED_TEXT_PNG_GENERATOR.

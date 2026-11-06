# ĐẶC TẢ NGHIỆP VỤ: CÔNG CỤ SINH ẢNH CHỮ TƯA RUA ĐA SẮC (FRAYED TEXT PNG GENERATOR)
<!-- Standards: Spec-Driven Development x Bát Khóa An Toàn v3.7 -->

## 1. Mục Tiêu & Bối Cảnh (Objective & Why)

- **Người dùng mục tiêu**: Đội ngũ thiết kế, sản xuất đồ họa áo đấu thể thao / áo bóng đá POD (Print-On-Demand) cần tạo nhanh các cụm chữ nghệ thuật mang hiệu ứng huy hiệu thêu viền xé vải (frayed chenille / embroidered patch).
- **Vấn đề cần giải quyết**: 
  - Trước đây, việc tạo viền chỉ may và tưa rua vải thủ công trên Photoshop tốn rất nhiều thời gian (15-30 phút/mẫu) hoặc phải dùng các texture cọ tĩnh dán đè xung quanh, dẫn đến việc khi đổi tên đội bóng (ví dụ từ `Hoffenheim` sang `Bayer Leverkusen`) thì viền bị méo mó, biến dạng hoặc đứt gãy.
  - Các công cụ thông thường bị gắn cứng màu (chỉ có màu trắng/đen) và không thể tự sinh tưa rua bên trong các lỗ hổng của chữ cái (`O`, `A`, `B`, `D`, `P`, `R`, `e`...).
- **Giá trị mang lại**: 
  - Tự động hóa hoàn toàn quy trình sinh đồ họa tưa rua chỉ trong tích tắc (< 1 giây).
  - Cho phép tùy biến độc lập toàn bộ bảng màu: Thân chữ, Viền trong, Viền ngoài, Đường chỉ thêu, và Sợi tưa rua.
  - Tự động thích ứng hình học 100% với bất kỳ độ dài chữ, font chữ, kích cỡ hay độ phức tạp của ký tự.

---

## 2. Tiêu Chí Nghiệm Thu Định Lượng (Quantitative Acceptance Criteria)

- [ ] `AC-01 (Tính Thích Ứng Hình Học Tự Động)`: Khi thay đổi chuỗi ký tự bất kỳ (từ ngắn như `BVB`, `REAL` đến dài như `Bayer Leverkusen`, `Hamburger SV`), toàn bộ 5 lớp đồ họa (Thân chữ, Viền trong, Viền ngoài, Đường chỉ may, Sợi tưa rua) phải tự động co giãn và bám theo chính xác đường biên thực tế của cụm chữ mới mà không cần chỉnh sửa thủ công.
- [ ] `AC-02 (Xử Lý Trọn Vẹn Lỗ Hổng Ký Tự - Inner Counters)`: Với các ký tự có khoảng trống rỗng khép kín bên trong (`A`, `B`, `D`, `O`, `P`, `R`, `a`, `e`, `g`...), cả đường chỉ may (dash stitch) và sợi tưa rua (fray) bắt buộc phải xuất hiện đầy đủ ở bên trong các lỗ hổng này tương tự như viền ngoài.
- [ ] `AC-03 (Tùy Biến Bảng Màu Độc Lập - Full Color Independence)`:
  - Cho phép đổi màu `text_color` (Màu thân chữ) độc lập qua mã HEX/RGB.
  - Cho phép đổi màu `inner_stroke_color` (Màu viền trong) độc lập qua mã HEX/RGB.
  - Cho phép đổi màu `outer_stroke_color` (Màu viền ngoài) độc lập qua mã HEX/RGB.
  - Cho phép đổi màu `dash_color` (Màu chỉ may) độc lập qua mã HEX/RGB.
  - Cho phép đổi màu `fray_color` (Màu sợi tưa rua) độc lập qua mã HEX/RGB.
- [ ] `AC-04 (Bản Chất Tưa Rua Sinh Thủ Tục - Procedural Fray Invariant)`:
  - Từng sợi tưa rua phải được sinh ra dựa trên vector pháp tuyến vuông góc với đường bao viền ngoài, có góc xòe ngẫu nhiên ($\pm 30^\circ - 45^\circ$) và chiều dài sợi ngẫu nhiên.
  - Tuyệt đối KHÔNG sử dụng hiệu ứng làm mờ (Blur), phát sáng (Glow), bóng đổ (Drop Shadow), hay dán texture ảnh tĩnh cố định.
- [ ] `AC-05 (Đường Chỉ Khâu Đều Đặn Theo Chu Vi)`: Đường nét đứt (Dash Stitch) phải phân bố đều đặn theo chiều dài thực của đường viền, không bị kéo dãn hay méo mó ở các đoạn cua gập khúc.
- [ ] `AC-06 (Tính Tái Lập Nhờ Random Seed)`: Khi giữ nguyên nội dung chữ, font, kích thước và cùng một số `random_seed`, kết quả tưa rua sinh ra phải giống nhau 100% giữa các lần render.
- [ ] `AC-07 (Định Dạng Đầu Ra & Độ Trong Suốt Tuyệt Đối)`: File xuất ra bắt buộc là ảnh PNG định dạng RGBA. Nền ngoài biên tưa rua phải là trong suốt 100% (Alpha = 0). Tuyệt đối không nung nền đen, trắng hay họa tiết bàn cờ xem trước vào file ảnh xuất.
- [ ] `AC-08 (Khả Năng Chống Treo & Validate Dữ Liệu)`: Khi người dùng nhập mã màu sai định dạng (ví dụ `#ZZZ`), chuỗi chữ rỗng hoặc font không tồn tại, hệ thống phải chặn lại và cảnh báo rõ ràng, tuyệt đối không bị sập (crash) ứng dụng.

---

## 3. Rào Chắn Ranh Giới (Boundaries & Scope Fencing)

### Bắt buộc có (Always Do):
- Tuân thủ thứ tự phân tầng thị giác chuẩn: `Nền Trong Suốt` -> `Sợi Tưa Rua (Fray)` -> `Viền Ngoài (Outer Stroke)` kết hợp `Chỉ May (Dash)` -> `Viền Trong (Inner Stroke)` -> `Thân Chữ (Text)`.
- Chống răng cưa mượt mà (Anti-Aliasing) cho tất cả các đường nét mảnh và sợi tưa rua.
- Tự động tính toán kích thước Canvas (Auto-fit Bounding Box + Padding) bao trọn toàn bộ sợi tưa rua xòe ra ngoài cùng.

### Phải hỏi ý kiến trước (Ask First):
- Thay đổi cấu trúc dữ liệu hoặc loại bỏ bất kỳ tham số màu/kích thước nào đã định nghĩa trong Master Plan.
- Bổ sung các hiệu ứng đồ họa phức tạp ngoài phạm vi (như đổ bóng 3D, họa tiết vải nền lót trong thân chữ).

### Tuyệt đối KHÔNG LÀM (Out-of-Scope / Never Do):
- **CẤM DÙNG AI IMAGE GENERATION (DALL-E, Midjourney...)**: Toàn bộ quá trình tạo ảnh phải là thuật toán hình học thủ tục toán học, xác định và lặp lại được.
- **Không hỗ trợ văn bản nhiều dòng (Multiline)** trong phiên bản V1 (chỉ tập trung tối đa cho Single-line Wordmark áo đấu).
- **Chưa làm xuất file PSD phân lớp** trong V1 (ưu tiên số 1 là ảnh trong suốt PNG chất lượng cao).
- **Không nhồi nhét xử lý hiệu ứng vào bounding box hình chữ nhật**: Mọi hiệu ứng phải bám chặt theo viền chữ.

---

## 4. Hợp Đồng Dữ Liệu Nghiệp Vụ (Business Data Contract)

| Trường dữ liệu | Kiểu dữ liệu | Bắt buộc | Giá trị mặc định | Quy tắc kiểm thực (Validation Rules) |
| :--- | :--- | :---: | :--- | :--- |
| `text` | Chuỗi ký tự | Có | `"Hoffenheim"` | Không được để trống hoặc chỉ chứa khoảng trắng. |
| `font_path` | Đường dẫn tệp | Có | Font hệ thống (Arial Bold) | Tệp font `.ttf` hoặc `.otf` phải tồn tại và đọc được. |
| `font_size` | Số nguyên | Có | `160` | Giá trị trong khoảng $[20, 600]\text{ px}$. |
| `letter_spacing`| Số thực/nguyên| Không | `2` | Khoảng cách chữ $\ge -20\text{ px}$. |
| `text_color` | Mã màu | Có | `"#1961B5"` | Chuỗi HEX 6 ký tự (`#RRGGBB`) hoặc cú pháp RGB hợp lệ. |
| `inner_stroke_color`| Mã màu | Có | `"#FFFFFF"` | Mã màu HEX/RGB hợp lệ. |
| `inner_stroke_width`| Số nguyên | Có | `4` | $\ge 0\text{ px}$. |
| `outer_stroke_color`| Mã màu | Có | `"#000000"` | Mã màu HEX/RGB hợp lệ. |
| `outer_stroke_width`| Số nguyên | Có | `16` | $\ge 0\text{ px}$. |
| `dash_color` | Mã màu | Có | `"#FFFFFF"` | Mã màu HEX/RGB hợp lệ. |
| `dash_length` | Số thực | Có | `10.0` | $> 0\text{ px}$. |
| `dash_gap` | Số thực | Có | `6.0` | $> 0\text{ px}$. |
| `dash_thickness`| Số thực | Có | `2.0` | $> 0\text{ px}$. |
| `fray_color` | Mã màu | Có | `"#FFFFFF"` | Mã màu HEX/RGB hợp lệ. |
| `fray_density` | Số thực | Có | `0.85` | Tỷ lệ lấy mẫu trong khoảng $[0.1, 1.0]$. |
| `fray_length` | Số thực | Có | `25.0` | Chiều dài sợi cơ bản $[2, 100]\text{ px}$. |
| `fray_randomness`| Số thực | Có | `0.65` | Độ phân tán $[0.0, 1.0]$. |
| `random_seed` | Số nguyên | Có | `42` | Số nguyên không âm để cố định biến ngẫu nhiên. |

*Nguyên tắc Fail-Closed*: Khi thiếu bất kỳ tham số tùy chọn nào, hệ thống tự động gán về giá trị mặc định chuẩn mực đã kiểm định; khi tham số cốt lõi sai định dạng, hệ thống từ chối thực thi và báo lỗi cụ thể, không tự ý đoán mò giá trị thay thế.

---

## 5. Rủi Ro Tiềm Ẩn & Biện Pháp Phòng Ngừa

> [!NOTE]
> 1. **Rủi ro sợi tưa rua bên trong lỗ nhỏ bị chồng chéo**: Ở các chữ có lỗ hổng rất hẹp (như mắt chữ `e` nhỏ), nếu chiều dài sợi tưa rua (`fray_length`) quá lớn, các sợi mọc từ hai bên mép lỗ hổng có thể đan chéo lấp kín lỗ.
>    - *Biện pháp*: Giữ nguyên tính tự nhiên này hoặc cho phép người dùng tùy chọn giới hạn chiều dài sợi tối đa dựa theo bán kính khoảng cách tâm (Distance Transform cap) nếu cần.
> 2. **Rủi ro hiệu năng khi tăng mật độ sợi**: Hàng chục nghìn sợi tưa rua vẽ chi tiết có thể làm chậm tốc độ hiển thị xem trước trực tiếp (Live Preview).
>    - *Biện pháp*: Thiết lập cơ chế tách biệt chất lượng xem trước (Preview dùng mật độ 50% có debounce 150ms) và chất lượng xuất xưởng (Export dùng 100% mật độ + Supersampling chống răng cưa cao cấp).

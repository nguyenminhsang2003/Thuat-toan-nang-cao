# Huffman-Text-Compressor

Nén và giải nén tệp văn bản bằng thuật toán **Huffman Coding** —
bài kiểm tra giữa kỳ môn **Thuật toán nâng cao**.

**Mã nguồn:** https://github.com/nguyenminhsang2003/Thuat-toan-nang-cao

## Cấu trúc thư mục

```
Thuat-toan-nang-cao/
├── huffman_coder.py     # mã nguồn chính (Python 3)
├── make_samples.py      # sinh lại các tệp văn bản mẫu
├── samples/             # tệp văn bản mẫu để chạy thử
│   ├── sample_vi.txt        # tiếng Việt có dấu (~24 KB)
│   ├── sample_en.txt        # tiếng Anh (~24 KB)
│   ├── sample_skewed.txt    # phân bố lệch: 1 ký tự chiếm ~70% (~12 KB)
│   └── *.huff               # (sau khi chạy demo) kết quả nén
├── report.md            # báo cáo lý thuyết + thực nghiệm
└── .gitignore
```

## Yêu cầu

- Python 3.7 trở lên
- Không cần cài thêm thư viện (dùng `heapq`, `collections.Counter`
  có sẵn trong thư viện chuẩn)

## Cách chạy

Tất cả lệnh thực hiện từ thư mục gốc của repo.

### 1. Chạy bộ kiểm thử

```bash
python huffman_coder.py test
```

In ra kết quả: PASS/FAIL cho từng trường hợp
(chỉ 1 ký tự, lặp lại, tiếng Việt, tệp rỗng, roundtrip byte-for-byte).

### 2. Nén tệp mẫu

```bash
python huffman_coder.py compress samples/sample_vi.txt samples/sample_vi.huff
```

Kết quả: in kích thước gốc, kích thước nén, tỷ lệ nén (%), số ký hiệu,
và tự động xác minh roundtrip (MATCH/MISMATCH).

### 3. Giải nén

```bash
python huffman_coder.py decompress samples/sample_vi.huff samples/sample_vi_dec.txt
```

### 4. Xem bảng mã + thống kê

```bash
python huffman_coder.py info samples/sample_vi.txt
```

In: tần suất từng ký tự, độ dài mã bit, mã của từng ký tự,
entropy lý tưởng, độ dài mã trung bình (so sánh với entropy).

### 5. Chạy demo trên toàn bộ samples

```bash
python huffman_coder.py demo
```

### 6. Tự định nghĩa tệp

```bash
python huffman_coder.py compress du_lieu.txt du_lieu.huff
python huffman_coder.py decompress du_lieu.huff phuc_hoi.txt
```

### 7. Sinh lại tệp mẫu (khuyến nghị chạy trước demo)

```bash
python make_samples.py
```

Tạo 3 tệp mẫu có kích thước vài chục KB — đủ lớn để chi phí bảng mã
(~3 byte/ký hiệu) được phân bổ, và **tỷ lệ nén phản ánh đúng hiệu quả
thực tế của thuật toán**. Nếu dùng tệp mẫu 2 KB, bảng mã chiếm phần lớn
dung lượng nên tỷ lệ nén bị bóp méo (chỉ 5–20%).

## Định dạng tệp `.huff` (tự mô tả)

Dùng **mã canonical**: tệp chỉ lưu *độ dài mã* của mỗi ký hiệu, hai bên cùng
tái tạo bảng mã bằng một quy tắc chung → phần đầu tệp rất gọn.

| Thành phần    | Kích thước       | Ghi chú                                        |
|---|---|---|
| Magic         | 4 byte (b"HUFF") | chống ghi nhầm tệp                             |
| version       | 1 byte (uint8)   | = 2                                            |
| n_symbols     | 2 byte (uint16)  | số ký hiệu phân biệt                           |
| pad           | 1 byte (uint8)   | số bit đệm cuối payload (0..7)                 |
| Bảng ký hiệu  | thay đổi         | mỗi ký hiệu: độ dài ký tự (1b) + ký tự + độ dài mã (1b) |
| payload       | thay đổi         | chuỗi bit đóng gói thành byte                  |

Giải nén hoàn toàn độc lập với tệp gốc — chỉ cần `.huff` duy nhất.

## Quy tắc mã canonical

1. Sắp các ký hiệu theo (độ dài mã tăng dần, mã điểm tăng dần).
2. Duyệt theo thứ tự đó, gán mã số liên tiếp; khi độ dài tăng từ L sang L'
   thì dịch mã sang trái (L'-L) bit.
3. Mã = biểu diễn nhị phân của số đó, đủ L' bit.

Kết quả là bảng mã **prefix-free** có đúng độ dài tối ưu của cây Huffman, và
bên giải nén tái tạo lại **giống hệt** bên nén mà không cần lưu chuỗi mã.

## Ghi chú về phương án B (Unicode)

- Đơn vị ký hiệu: **mã điểm Unicode**, không phải byte thô.
- Đọc tệp ở chế độ `text` (UTF-8), mỗi ký tự là 1 ký hiệu.
- Tỷ lệ nén đạt được cao hơn nhiều so với phương án byte thô, vì tần suất
  được gom về cấp ký tự thay vì cấp byte UTF-8.
- Số ký hiệu thực tế n thường 40–90 (không phải 256).
- Tiệm cận: Θ(N + n log n) ≈ Θ(N) khi n cố định.

## Kết quả mẫu (đo thực tế — `python make_samples.py` rồi `python huffman_coder.py demo`)

| Tệp mẫu           | Gốc (bytes) | Nén (bytes) | Tỷ lệ nén | n ký hiệu | Round-trip |
|---|---|---|---|---|---|
| `sample_vi.txt`   | 25 647 | 12 272 | **52,15%** | 94 | MATCH |
| `sample_en.txt`   | 24 016 | 13 196 | **45,05%** | 44 | MATCH |
| `sample_skewed.txt` | 12 079 | 2 358 | **80,48%** | 27 | MATCH |

Với `sample_vi.txt`: entropy `H = 4,9464` bit/ký tự, độ dài mã trung bình của
Huffman `L = 4,9839` bit/ký tự — chênh lệch chỉ **0,0375 bit/ký tự**, tức
mã Huffman đạt gần đúng cận lý tưởng của bài toán mã hóa ký hiệu theo ký hiệu.

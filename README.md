# Huffman-Text-Compressor

Nén và giải nén tệp văn bản bằng thuật toán **Huffman Coding** —
bài kiểm tra giữa kỳ môn **Thuật toán nâng cao**.

**Mã nguồn:** https://github.com/nguyenminhsang2003/Thuat-toan-nang-cao

## Cấu trúc thư mục

```
Thuat-toan-nang-cao/
├── huffman_coder.py     # mã nguồn chính (Python 3)
├── make_samples.py      # sinh các tệp văn bản mẫu
├── samples/             # tệp văn bản mẫu và kết quả nén
│   ├── sample_vi.txt        # tiếng Việt có dấu (~24 KB)
│   ├── sample_en.txt        # tiếng Anh (~24 KB)
│   ├── sample_skewed.txt    # phân bố lệch: 1 ký tự chiếm ~70% (~12 KB)
│   ├── sample_vi.huff
│   ├── sample_en.huff
│   └── sample_skewed.huff
├── report.md            # báo cáo
└── .gitignore
```

## Yêu cầu

- Python 3.7 trở lên
- Không cần cài thêm thư viện ngoài (dùng `heapq` và `collections.Counter`
  có sẵn trong thư viện chuẩn)

## Hướng dẫn chạy

Tất cả lệnh thực hiện từ thư mục gốc của repo.

### Chạy bộ kiểm thử

```bash
python huffman_coder.py test
```

### Nén tệp

```bash
python huffman_coder.py compress samples/sample_vi.txt samples/sample_vi.huff
```

In ra kích thước gốc, kích thước nén, tỷ lệ nén, số ký hiệu và tự động
xác minh round-trip (`MATCH` / `MISMATCH`).

### Giải nén tệp

```bash
python huffman_coder.py decompress samples/sample_vi.huff ket_qua.txt
```

### Xem bảng mã và thống kê

```bash
python huffman_coder.py info samples/sample_vi.txt
```

In ra tần suất từng ký tự, độ dài mã, mã của từng ký tự, entropy và độ
dài mã trung bình.

### Chạy demo trên toàn bộ tệp mẫu

```bash
python huffman_coder.py demo
```

### Sinh lại tệp mẫu

```bash
python make_samples.py
```

### Nén / giải nén tệp bất kỳ

```bash
python huffman_coder.py compress du_lieu.txt du_lieu.huff
python huffman_coder.py decompress du_lieu.huff phuc_hoi.txt
```

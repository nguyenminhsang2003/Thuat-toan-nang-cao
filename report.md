# BÁO CÁO BÀI KIỂM TRA GIỮA KỲ
## Môn: Thuật toán nâng cao — Huffman Codes & Data Compression

**Câu 1:** Vận dụng kiến thức Huffman Codes và Data Compression, thực hiện
nén dữ liệu cho tệp văn bản.

**Phương án thực hiện:** Tệp văn bản (`.txt`) — ngôn ngữ lập trình Python.

---

## 0. Định hướng thiết kế

| Quyết định | Lựa chọn | Lý do |
|---|---|---|
| Loại dữ liệu | Tệp văn bản `.txt` (UTF-8) | Dễ kiểm chứng kết quả: giải nén ra so sánh byte-for-byte với bản gốc |
| Ngôn ngữ | Python 3 | Có sẵn `heapq` (Min-Heap) và `collections.Counter` trong thư viện chuẩn |
| **Đơn vị ký hiệu** | **Mã điểm Unicode (phương án B)** | Tần suất gom về cấp *ký tự* thay vì cấp *byte UTF-8* ⇒ tỷ lệ nén cao hơn nhiều; `n` nhỏ hơn nhiều ⇒ phân tích tiệm cận rõ ràng hơn |

**Ghi chú quan trọng:** nếu nén ở mức *byte thô*, chữ có dấu tiếng Việt (ví dụ
"ế") bị tách thành 3 byte riêng biệt, khiến cây Huffman luôn có 256 lá và tỷ lệ
nén chỉ đạt khoảng 15–20%. Với phương án B, mỗi chữ là một ký hiệu duy nhất,
tần suất tập trung vào các chữ phổ biến, và tỷ lệ nén đo được trên tệp mẫu
tiếng Việt là **52,15%**. Đây là lựa chọn thiết kế có chủ đích, được giải
trình trong báo cáo.

---

## a. TRÌNH BÀY THUẬT TOÁN

### a.1. Nguyên lý chung

Huffman coding là phương pháp nén dữ liệu không mất thông tin (lossless) theo
nguyên tắc: **ký hiệu xuất hiện càng nhiều thì mã càng ngắn**. Thuật toán sinh ra
một *mã tiền tố* (prefix code) — trong đó không mã nào là tiền tố của mã khác —
nhờ đó chuỗi mã nhị phân có thể giải mã ngược lại chính xác, không mơ hồ.

### a.2. Thuật toán nén (4 bước)

```
BƯỚC 1: Đếm tần suất        BƯỚC 2: Dựng Min-Heap & Cây Huffman
──────────────────────        ────────────────────────────────
Đọc tệp .txt (UTF-8)          freq = Counter(text)          // Θ(N)
text → chuỗi ký tự            heap = [(f, i, Node) cho mỗi ký hiệu]
freq[ch] = số lần xuất hiện   heapq.heapify(heap)           // Θ(n)
                              lặp khi heap còn > 1 node:
                                  left  = heappop(heap)     // nhỏ nhất
                                  right = heappop(heap)     // nhỏ nhất thứ 2
                                  push(Node(f_left+f_right, left, right))
                              gốc = heap[0]

BƯỚC 3: Tạo bảng mã         BƯỚC 4: Ghi bit ra tệp
──────────────────────        ────────────────────────────────
DFS từ gốc để lấy ĐỘ DÀI:     với mỗi ký tự trong text:
  rẽ trái  → độ dài +1           ghi mã canonical của nó vào bit-stream
  rẽ phải  → độ dài +1         đóng gói: 8 bit → 1 byte
  tới lá   → length[ch] = d    ghi header (magic, version, n, pad, bảng độ dài)
                               ghi payload
⇒ mã CANONICAL (tái tạo từ độ dài, không lưu chuỗi mã)
```

### a.2.1. Mã canonical — kỹ thuật tối ưu phần đầu tệp

Nếu lưu trực tiếp chuỗi mã của từng ký hiệu vào tệp, mỗi ký hiệu tốn
~5–10 byte (mã hiệu + độ dài + chuỗi mã). Với một tệp có 91 ký hiệu, phần
đầu tệp có thể chiếm gần một nửa dung lượng, và tỷ lệ nén bị tệ hại dù
thuật toán hoàn toàn đúng.

Giải pháp là **mã canonical** (canonical Huffman): tệp chỉ lưu *độ dài mã*
của mỗi ký hiệu, còn hai bên nén và giải nén cùng tuân theo một quy tắc
tái tạo mã:

1. Sắp các ký hiệu theo **độ dài mã tăng dần**, khi trùng thì theo **mã điểm
   tăng dần**.
2. Duyệt theo thứ tự đó, gán các số nguyên liên tiếp `0, 1, 2, ...`; khi độ
   dài tăng từ `L` sang `L'` thì **dịch số sang trái `L' - L` bit**.
3. Mã của ký hiệu là biểu diễn nhị phân của số đó, viết đủ `L'` bit.

Nhờ vậy bảng mã vẫn **prefix-free** và có **đúng độ dài tối ưu** của cây
Huffman, nhưng phần đầu tệp chỉ tốn ~3 byte/ký hiệu, và bên giải nén tái tạo
lại bảng mã **giống hệt** bên nén mà không cần lưu bất kỳ chuỗi mã nào.

Đây chính là kỹ thuật mà các định dạng thực tế như **DEFLATE** (trong ZIP) và
**JPEG** sử dụng.

### a.3. Cây Huffman — ví dụ minh họa

Xét chuỗi `A B B A C A` (tần suất: A=3, B=2, C=1):

```
Bước gộp 1:  C(1) + B(2) → CB(3)      Bước gộp 2:  CB(3) + A(3) → root(6)
```

Cây kết quả:

```
              root (6)
             /          \
          A(3)          CB(3)
                      /      \
                   B(2)    C(1)
```

Bảng mã sinh ra (duyệt gốc → lá):

| Ký tự | Tần suất | Mã | Độ dài |
|---|---|---|---|
| A | 3 | `0` | 1 |
| B | 2 | `10` | 2 |
| C | 1 | `11` | 2 |

Bảng mã này **prefix-free**: `0`, `10`, `11` — không mã nào là tiền tố của mã khác.
Chuỗi gốc `A B B A C A` mã hoá thành `0 10 10 0 11 0` = `010100110` (9 bit,
thay vì 18 bit nếu dùng mã cố định 2 bit/ký tự).

Quan sát: ký tự tần suất cao nhất (A) nhận mã ngắn nhất (`0`), ký tự tần suất
thấp nhất (C) nhận mã dài nhất — đúng nguyên lý của Huffman.

### a.4. Thuật toán giải nén

```
1. Đọc header: magic "HUFF", version, n_symbols, pad
2. Đọc bảng ký hiệu → dict {ký tự: độ dài mã}
3. Tái tạo bảng mã CANONICAL từ các độ dài (cùng quy tắc ở mục a.2.1)
   ⇒ thu được đúng bảng mã mà bên nén đã dùng
4. Đọc payload → giải mã từng byte ra chuỗi bit (bỏ `pad` bit cuối)
5. Duyệt bit từ trái sang phải:
       nối bit vào bộ đệm; nếu bộ đệm khớp một mã hoàn chỉnh trong bảng
       → ghi ký tự tương ứng và xóa bộ đệm
6. Ghi chuỗi ký tự ra tệp .txt (UTF-8)
```

Bảng độ dài được nhúng ngay trong tệp `.huff`, nên **quá trình giải nén hoàn
toàn độc lập với tệp gốc** — chỉ cần tệp `.huff` là đủ.

### a.4.1. Định dạng tệp `.huff`

| Thành phần   | Kích thước      | Nội dung                                        |
|---|---|---|
| Magic        | 4 byte          | `b"HUFF"` — chống ghi nhầm tệp                 |
| version      | 1 byte          | `2` — số phiên bản định dạng                   |
| n_symbols    | 2 byte (uint16) | số ký hiệu phân biệt `n`                       |
| pad          | 1 byte (uint8)  | số bit đệm cuối payload (0..7)                 |
| Bảng ký hiệu | `3n` byte xấp xỉ | mỗi ký hiệu: độ dài ký tự UTF-8 (1b) + ký tự + độ dài mã (1b), sắp theo mã điểm tăng dần |
| payload      | thay đổi        | chuỗi bit đã đóng gói thành byte (đệm 0 ở cuối) |

### a.5. Các trường hợp biên được xử lý

| Trường hợp | Xử lý |
|---|---|
| Chỉ **một ký hiệu duy nhất** | Cây chỉ có 1 nút, mã gán cố định `"0"` (không để mã rỗng — mỗi ký tự vẫn tốn 1 bit) |
| **Tệp rỗng** | Không có ký hiệu nào để nén; header ghi `n=0`, `pad=0`, payload rỗng; giải nén ra tệp rỗng |
| Số bit **không chia hết cho 8** | Ghi số bit đệm (`pad`, 0..7) vào header để giải nén biết chỗ nào là padding |
| Tệp `.huff` **không hợp lệ** | Kiểm tra magic `"HUFF"` → ném lỗi rõ ràng thay vì crash |
| **Dòng mới trên Windows** | Mở/ghi tệp với `newline=""` để ngăn Windows tự dịch thuật `\n` ⇄ `\r\n` (text-mode) — nếu không thì round-trip sai byte-for-byte |

---

## b. TÍNH TOÁN CÁC GIÁ TRỊ O, Ω, Θ

Ký hiệu: `N` = tổng số ký tự của tệp văn bản, `n` = số ký hiệu phân biệt
(`n ≤ N`, và trong văn bản thực tế `n` chỉ khoảng 30–95 theo đo ở mục c.1),
`L` = độ dài mã trung bình (bit/ký tự).

### b.1. Phân tích từng bước

| Bước | Thời gian | Giải thích |
|---|---|---|
| Đọc tệp + đếm tần suất (`Counter` = bảng băm) | **Θ(N)** | phải duyệt qua N ký tự |
| `heapq.heapify` (dựng Min-Heap từ n nút) | **Θ(n)** | heapify của Floyd chạy O(n), *không* phải O(n log n) |
| n−1 lần `heappop` × 2 + `heappush` | **Θ(n log n)** | mỗi thao tác O(log n), tổng cộng (n−1) lần |
| Duyệt cây để lấy độ dài mã (DFS) | **Θ(n)** | duyệt hết n lá, mỗi lá một độ dài |
| Sắp xếp + tái tạo mã canonical | **Θ(n log n)** | sắp n ký hiệu theo (độ dài, mã điểm) |
| Mã hoá N ký tự (sinh N đoạn mã) | **Θ(N·L)** | tổng số bit ghi ra = Σ len(code[ch]) = N·L |
| Đóng gói bit → byte | **Θ(N·L)** | quét từng bit một lần |
| Ghi/đọc tệp | **Θ(N·L)** | tuyến tính theo số bit |

Vì mã là prefix-code, ta có **L ≤ log₂ n** (tính chất cây Huffman với trọng số
tần suất), suy ra `Θ(N·L) = Θ(N log n)`.

### b.2. Tổng hợp

Thời gian tổng quát:

```
T(N, n) = Θ(N) + Θ(n log n) + Θ(N log n) = Θ(N + n log n)
```

Do đó:

- **O(N + n log n)** — cận trên.
- **Ω(N)** — cận dưới: bất kỳ thuật toán nén nào cũng phải đọc qua N ký tự
  để xác định được tần suất, nên không thể chạy nhanh hơn tuyến tính.
- **Θ(N + n log n)** — cận chặt trong trường hợp tổng quát (N và n thay đổi
  độc lập, ví dụ n = Θ(N)).

### b.3. Khi n cố định — trường hợp thực tế của bài toán

Tập ký hiệu là **mã điểm Unicode**, nên `n` có trần cố định (1 114 112 mã điểm),
và trong văn bản thực tế `n` chỉ khoảng 30–95 (đo được: 94 với tiếng Việt,
44 với tiếng Anh) — hằng số rất nhỏ so với N. Khi đó `n log n` là hằng số, và:

```
T(N) = Θ(N + n log n) = Θ(N)
```

**Kết luận (theo đúng ký hiệu đề bài yêu cầu):**
`O(N + n log n)`, `Ω(N)`, và `Θ(N)` khi xem `n` là hằng số — tức là tiệm cận
tuyến tính theo độ dài tệp.

> Bản chất: thuật toán đạt **tuyến tính** theo kích thước dữ liệu, đây là tính
> chất tốt nhất có thể vì bắt buộc phải đọc hết tệp.

### b.4. Độ phức tạp bộ nhớ

| Thành phần | Bộ nhớ |
|---|---|
| Cây Huffman | `2n − 1` nút ⇒ **O(n)** nút |
| Bảng độ dài mã (n ký hiệu) | **O(n)** |
| Bảng mã tái tạo (n chuỗi bit) | **O(n log n)** bit |
| Chuỗi `text` đã nạp vào RAM | **O(N)** ký tự — do cách đọc tệp một lần |
| Chuỗi bit sinh ra khi mã hóa | **O(N·L)** bit |

Tổng theo cách hiện tại: **O(N + n log n)**. Lưu ý phần phụ thuộc `N` đến từ
thói quen nạp toàn bộ tệp vào bộ nhớ để đếm tần suất, **không phải bản chất
của thuật toán dựng cây** — về lý thuyết có thể đếm tần suất theo dòng
(streaming) và dựng cây song song, khi đó bộ nhớ phụ thuộc N chỉ còn O(n)
cộng một buffer đọc cố định.

---

## c. ĐÁNH GIÁ ĐỘ PHỨC TẠP THUẬT TOÁN

### c.1. Kết quả thực nghiệm

> **Cách chạy lấy số liệu:**
> ```bash
> python make_samples.py                          # 1. sinh tệp mẫu
> python huffman_coder.py demo                    # 2. nén + xác minh
> python huffman_coder.py info samples/sample_vi.txt   # 3. bảng mã + entropy
> ```

<!-- SỐ LIỆU THỰC NGHIỆM - đã chạy thực tế, xem bên dưới -->

| Tệp mẫu | Đặc điểm | Kích thước gốc (bytes) | Kích thước nén (bytes) | Tỷ lệ nén | n ký hiệu | Round-trip |
|---|---|---|---|---|---|---|
| `sample_vi.txt` | Tiếng Việt có dấu | 25 647 | 12 272 | **52,15%** | 94 | MATCH |
| `sample_en.txt` | Tiếng Anh | 24 016 | 13 196 | **45,05%** | 44 | MATCH |
| `sample_skewed.txt` | Phân bố lệch (1 ký tự ~70%) | 12 079 | 2 358 | **80,48%** | 27 | MATCH |

Công thức tỷ lệ nén dùng trong báo cáo:

```
Tỷ lệ nén (%) = (1 − S_nén / S_gốc) × 100%
```

**Vì sao tệp mẫu phải đủ lớn.** Huffman có một chi phí cố định là **bảng mã**
(~3 byte/ký hiệu, không phụ thuộc độ dài tệp). Trên tệp chỉ 2 KB, bảng mã
chiếm gần một nửa dung lượng, nên tỷ lệ nén bị bóp méo xuống còn 5–20% —
**không phản ánh hiệu quả thuật toán mà phản ánh chi phí khởi tạo**. Khi tệp
đủ lớn vài chục KB, chi phí này được phân bổ và tỷ lệ nén phản ánh đúng
hiệu quả thực tế. Vì vậy chương trình sinh tệp mẫu ~24 KB cho hai tệp văn
bản tự nhiên.

### c.1.1. Độ dài mã so với entropy (tệp `sample_vi.txt`)

Kết quả lệnh `python huffman_coder.py info samples/sample_vi.txt`:

| Đại lượng | Giá trị |
|---|---|
| Số ký tự | 19 080 |
| Số ký hiệu phân biệt `n` | 94 |
| Entropy `H` (cận dưới lý tưởng) | **4,9464 bit/ký tự** |
| Độ dài mã trung bình `L` (Huffman) | **4,9839 bit/ký tự** |
| Chênh lệch `L − H` | **0,0375 bit/ký tự** |
| Tổng số bit dữ liệu | 95 092 bit (≈ 11 887 byte) |
| Tổng số bit nếu dùng mã cố định 8 bit | 152 640 bit (≈ 19 080 byte) |

Chênh lệch chỉ **0,0375 bit/ký tự** — tức mã Huffman đạt gần đúng cận lý tưởng
của bài toán mã hóa ký hiệu theo ký hiệu. (Định lý Shannon: `H ≤ L < H + 1`
khi `n` là lũy thừa của 2, và `H ≤ L < H + 2` nói chung.)

Một số dòng trong bảng mã thực tế sinh ra:

| Ký tự | Tần suất | Độ dài mã | Mã |
|---|---|---|---|
| (dấu cách) | 4 119 | 2 | `00` |
| `n` | 1 787 | 3 | `010` |
| `h` | 1 333 | 4 | `0111` |
| `c` | 913 | 4 | `0110` |
| `t` | 872 | 5 | `10010` |
| `u` | 441 | 6 | `101011` |
| `à` | 317 | 6 | `101101` |
| `đ` | 268 | 6 | `101110` |
| `.` | 221 | 7 | `1100010` |
| `ế` | 104 | 8 | `11101010` |

Quan sát đáng chú ý: dấu cách (tần suất cao nhất) chỉ tốn **2 bit**, còn các
ký tự hiếm như `ế` tốn tới **8 bit**. Đó chính là cơ chế của Huffman — mã
được phân bổ theo xác suất, không phải đồng đều.

### c.2. Nhận xét

1. **Tỷ lệ nén phụ thuộc phân bố tần suất, không phụ thuộc độ dài tệp.**
   `sample_skewed.txt` đạt **80,48%** vì tần suất tập trung mạnh vào một ký
   tự; `sample_vi.txt` đạt 52,15% vì bảng chữ cái phân bố đều hơn; và
   `sample_en.txt` chỉ 45,05% vì bảng chữ cái Latin phân bố đều hơn nữa và
   có nhiều nguyên âm tần suất gần bằng nhau. Đây chính là đặc tính của
   Huffman: **tần suất càng lệch, nén càng hiệu quả**.

2. **Độ dài mã thực tế rất gần entropy.** Với `sample_vi.txt`: `H = 4,9464`
   còn `L = 4,9839` — chênh lệch chỉ **0,0375 bit/ký tự**. Với định lý Shannon,
   `H ≤ L < H + 1` khi `n` là lũy thừa của 2, và `H ≤ L < H + 2` nói chung.
   Đây là lý do Huffman là mã tối ưu theo nghĩa **trung bình ký hiệu**.

3. **Huffman vượt trội Fixed-length Code (mã cố định).** Với `sample_vi.txt`
   có 94 ký hiệu phân biệt, mã cố định cần **7 bit/ký tự**
   (⌈log₂94⌉ = 7) cho mọi ký tự — tức 133 560 bit. Huffman chỉ dùng 95 092
   bit, tiết kiệm **28,8%** số bit so với mã cố định, và 37,7% so với mã
   8 bit/ký tự. Chênh lệch này càng lớn khi phân bố tần suất càng lệch.

4. **So với phương án byte thô:** nếu nén ở mức byte, tỷ lệ nén chỉ khoảng
   15–20% vì byte UTF-8 của chữ có dấu rất phân tán. Phương án B (mã điểm
   Unicode) cho tỷ lệ nén gấp 2–3 lần với cùng một thuật toán — đây là minh
   chứng rõ ràng cho lựa chọn thiết kế ở mục 0.

5. **Giới hạn của Huffman đơn thuần:** bảng mã phải được truyền kèm dữ liệu.
   Với tệp nhỏ, phần bảng mã có thể chiếm tỷ lệ đáng kể (ví dụ tệp chỉ vài
   chữ); khi đó tổng dung lượng có thể **lớn hơn** tệp gốc. Trong bài này đã
   xử lý bằng **mã canonical** (chỉ lưu độ dài mã, ~3 byte/ký hiệu thay vì
   ~10), và bằng cách dùng tệp mẫu đủ lớn. Giải pháp triệt để hơn trong thực
   tế là kết hợp Huffman với LZ77 (như **DEFLATE** trong ZIP/GZIP).

6. **Kinh nghiệm rút ra từ quá trình kiểm thử.** Trong quá trình phát triển,
   hai lỗi đã được bộ kiểm thử tự động phát hiện:
   - *Bảng mã bị đảo chiều.* Bản đầu tiên lưu bảng mã theo hướng `{mã: ký tự}`
     khi đọc từ tệp, trong khi phần giải mã mong đợi `{ký tự: mã}` — kết quả
     là file giải nén ra **rỗng hoàn toàn**. Lỗi này không lộ ra khi test bằng
     chuỗi nội tại, chỉ lộ ra khi test round-trip trên tệp thật.
   - *Dịch thuật dòng mới trên Windows.* Mở/ghi tệp ở chế độ text thường khiến
     Windows tự đổi `\n` ⇄ `\r\n`, làm round-trip sai byte-for-byte. Khắc
     phục bằng tham số `newline=""`.

   → Bài học: **mọi thuật toán nén đều phải có kiểm thử round-trip byte-for-byte**,
   vì "chạy không lỗi" khác hoàn toàn với "giải mã đúng".

### c.3. Tính đúng đắn

- **Bảng mã prefix-free** → giải mã không mơ hồ: mỗi chuỗi bit đọc được
  xác định duy nhất một ký tự.
- **Điều kiện Kraft:** tổng `Σ 2^(−len)` của các độ dài mã luôn `≤ 1` — là
  điều kiện cần và đủ để tồn tại một cây prefix-code. Bộ kiểm thử kiểm tra
  điều này cho mọi cây Huffman sinh ra.
- **Round-trip byte-for-byte:** sau khi nén, chương trình tự giải nén ra tệp
  tạm và so sánh với tệp gốc — lệnh `compress` in ra `ROUND-TRIP: MATCH`.
- **Bộ kiểm thử nội tại** (`python huffman_coder.py test`) gồm 11 kiểm tra:
  6 trường hợp chuỗi (1 ký tự, lặp lại, chuỗi kinh điển, tiếng Việt, đủ ký
  tự tiếng Việt, từ lặp nhiều) với kiểm tra prefix-free + round-trip; tái tạo
  mã canonical từ độ dài; điều kiện Kraft; canonical giữ nguyên độ dài mã;
  round-trip trên tệp thật; và tệp rỗng.

---

## d. TÀI LIỆU THAM KHẢO

1. Huffman, D. A. (1952). *A Method for the Construction of Minimum-Redundancy
   Codes*. IRE Transactions on Information Theory, 4(3), 83–87.
2. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009).
   *Introduction to Algorithms* (3rd ed.), Chapter 16 — Greedy Algorithms.
3. Shannon, C. E. (1948). *A Mathematical Theory of Communication*.
4. W3C. *Unicode Standard — Chapter 3: Conformance, U+0000..U+10FFFF*.

## e. LIÊN KẾT MÃ NGUỒN

**GitHub Repository:** https://github.com/nguyenminhsang2003/Thuat-toan-nang-cao

Bài kiểm tra giữa kỳ môn Thuật toán nâng cao — Huffman Codes & Data Compression.
Mã nguồn Python, có kèm bộ kiểm thử tự động và các tệp nén mẫu.

```
Thuat-toan-nang-cao/
├── huffman_coder.py       # mã nguồn chính
├── make_samples.py        # sinh tệp văn bản mẫu
├── README.md
├── report.md
├── .gitignore
└── samples/
    ├── sample_vi.txt
    ├── sample_en.txt
    ├── sample_skewed.txt
    ├── sample_vi.huff
    ├── sample_en.huff
    └── sample_skewed.huff
```

# BÁO CÁO BÀI KIỂM TRA GIỮA KỲ — THUẬT TOÁN NÂNG CAO

**Họ và tên:** Nguyễn Minh Sáng
**Lớp:** 34CNTT11
**Môn:** Thuật toán nâng cao
**Đề bài:** Câu 1 — Vận dụng kiến thức Huffman Codes và Data Compression, thực hiện nén dữ liệu cho một số loại dữ liệu: tệp văn bản, tệp âm thanh, tệp ảnh.

**Phương án thực hiện:** Tệp văn bản (`.txt`) — ngôn ngữ Python.
**Mã nguồn:** https://github.com/nguyenminhsang2003/Thuat-toan-nang-cao

---

## 1. Trình bày thuật toán

### 1.1. Nguyên lý chung

Huffman coding là phương pháp nén dữ liệu **không mất thông tin** (lossless), dựa trên nguyên tắc: **ký hiệu xuất hiện càng nhiều trong văn bản thì mã biểu diễn càng ngắn**. Người ta dùng một cây nhị phân để gán mã nhị phân cho từng ký hiệu sao cho tổng số bit nhỏ nhất.

Điểm mấu chốt để mã hóa được là **tính chất tiền tố** (prefix-free): bảng mã được sinh ra phải bảo đảm không mã nào là tiền tố của mã khác. Nhờ vậy, khi đọc chuỗi bit từ trái sang phải, mỗi khi gặp một dãy bit khớp trọn vẹn với một mã trong bảng thì ta biết chắc chắn ký tự tương ứng — không có khả năng nhập nhằng. Đây là điều kiện cần và đủ để việc giải mã là đơn ánh.

**Đơn vị ký hiệu.** Tôi chọn nén ở mức **ký tự Unicode** chứ không phải byte thô. Chữ có dấu tiếng Việt như "ế" chiếm 2 byte trong UTF-8; nếu nén ở mức byte thì mỗi chữ bị tách thành 2 ký hiệu riêng biệt, cây Huffman luôn có 256 lá với tần suất rất phân tán. Ở mức ký tự, tần suất dồn vào khoảng 90 chữ phổ biến và tỷ lệ nén cao hơn hẳn: **52,15%** với tệp mẫu tiếng Việt, so với khoảng 15–20% nếu nén ở mức byte. Ngoài ra, ở mức ký tự số ký hiệu phân biệt `n` nhỏ hơn nhiều, nên phân tích độ phức tạp ở mục 2 cũng rõ ràng hơn.

### 1.2. Thuật toán nén (4 bước)

```
BƯỚC 1: Đếm tần suất
  Đọc tệp .txt (UTF-8) → chuỗi ký tự text
  freq[ch] = số lần xuất hiện của ch trong text      // Θ(N)

BƯỚC 2: Dựng Min-Heap và cây Huffman
  heap = [(freq, tiebreak, Node) cho mỗi ký hiệu]
  heapq.heapify(heap)                                 // Θ(n)
  lặp khi heap còn > 1 nút:
      left  = heappop(heap)      // nút nhẹ nhất trong heap
      right = heappop(heap)      // nút nhẹ nhất thứ hai
      push(Node(left.freq + right.freq, left, right))
  gốc = heap[0]       // cây Huffman đã hoàn chỉnh (2n-1 nút)

BƯỚC 3: Tạo bảng mã
  DFS từ gốc để lấy độ dài mã:
      rẽ trái  → độ dài + 1
      rẽ phải  → độ dài + 1
      tới lá   → length[ch] = độ dài đường đi
  Sau đó dựng mã canonical từ bảng độ dài (xem mục 1.5)
  ⇒ bảng mã PREFIX-FREE

BƯỚC 4: Ghi bit ra tệp
  Với mỗi ký tự trong text: ghi mã của nó vào chuỗi bit
  Đóng gói 8 bit → 1 byte (bit cuối đệm 0)
  Ghi header: magic + version + n_symbols + pad + bảng ký hiệu
  Ghi payload
```

**Vì sao dùng Min-Heap.** Thuật toán Huffman cần liên tục tìm hai nút có trọng số nhỏ nhất trong tập các nút đang chờ gộp. Nếu duyệt tuyến tính mỗi lần thì tổng thời gian là O(n²). Min-Heap cho phép lấy ra phần tử nhỏ nhất và chèn phần tử mới trong O(log n), nên toàn bộ quá trình gộp chỉ mất O(n log n).

**Vì sao phải có tie-breaker.** Trong `heapq`, các phần tử được so sánh bằng toán tử `<`. Nếu hai ký hiệu có cùng tần suất (rất hay xảy ra, ví dụ hai nguyên âm "a" và "e" cùng xuất hiện 100 lần) thì chương trình sẽ thử so sánh hai đối tượng `HuffmanNode` với nhau và gây lỗi `TypeError`. Tôi khắc phục bằng cách lưu mỗi nút trong heap dưới dạng tuple `(tần suất, số thứ tự, node)` — số thứ tự luôn khác nhau nên không bao giờ phải so sánh node.

### 1.3. Ví dụ minh họa

Xét chuỗi `A B B A C A` với tần suất A = 3, B = 2, C = 1.

**Bước gộp 1:** hai nút nhẹ nhất là C(1) và B(2), gộp thành CB(3).

```
heap ban đầu:  C(1)  B(2)  A(3)
           →   CB(3)  A(3)
```

**Bước gộp 2:** hai nút nhẹ nhất là CB(3) và A(3), gộp thành root(6).

```
           →   root(6)
```

 Cây Huffman hoàn chỉnh:

```
              root (6)
             /          \
          A(3)          CB(3)
                      /      \
                   B(2)    C(1)
```

Bảng mã sinh ra:

| Ký tự | Tần suất | Đường đi từ gốc | Mã | Độ dài |
|---|---|---|---|---|
| A | 3 | trái | `0` | 1 |
| B | 2 | phải-trái | `10` | 2 |
| C | 1 | phải-phải | `11` | 2 |

Bảng mã này prefix-free: không mã nào là tiền tố của mã khác (`0` không phải tiền tố của `10` hay `11`; `10` và `11` khác nhau ở bit cuối).

Chuỗi gốc `A B B A C A` mã hóa thành:

```
A  B  B  A  C  A
0  10 10 0  11 0
→ 010100110  (9 bit)
```

So với mã cố định 2 bit/ký tự thì cần 12 bit, so với ASCII 8 bit/ký tự thì cần 48 bit. Chú ý hai điều:

- Ký tự tần suất cao nhất (A) nhận mã **ngắn nhất** (`0`), ký tự tần suất thấp nhất (C) nhận mã dài nhất — đúng nguyên lý của Huffman.
- Mã ngắn nhất không bao giờ rỗng: kể cả khi chỉ có một ký tự duy nhất trong tệp thì mã của nó vẫn là `0` (1 bit), nếu để rỗng thì không thể giải mã được.

### 1.4. Thuật toán giải nén

```
1. Đọc header: magic "HUFF", version, n_symbols, pad
2. Đọc bảng ký hiệu → dict {ký tự: độ dài mã}
3. Tái tạo bảng mã canonical từ các độ dài (cùng quy tắc ở bên nén)
   ⇒ thu được đúng bảng mã mà bên nén đã dùng
4. Đọc payload → chuỗi bit (bỏ `pad` bit đệm ở cuối)
5. Duyệt bit từ trái sang phải:
       nối bit vào bộ đệm
       nếu bộ đệm khớp một mã hoàn chỉnh trong bảng
          → ghi ký tự tương ứng, xóa bộ đệm
6. Ghi chuỗi ký tự ra tệp .txt (UTF-8)
```

Nhờ tính prefix-free, ở bước 5 có **duy nhất một** mã khớp tại mỗi thời điểm, nên quá trình giải mã luôn xác định.

Bảng độ dài được nhúng ngay trong tệp `.huff`, do đó **quá trình giải nén hoàn toàn độc lập với tệp gốc** — chỉ cần tệp `.huff` là đủ để khôi phục lại nội dung.

### 1.5. Mã canonical và định dạng tệp `.huff`

**Vấn đề:** nếu lưu trực tiếp chuỗi mã của từng ký hiệu vào tệp thì mỗi ký hiệu tốn khoảng 10 byte (mã hiệu 4 byte + độ dài 1 byte + chuỗi mã dạng ký tự ASCII). Với 94 ký hiệu, phần đầu tệp sẽ chiếm gần 1 KB — đủ để làm hỏng tỷ lệ nén dù thuật toán hoàn toàn đúng.

**Giải pháp — mã canonical** (canonical Huffman): tệp chỉ lưu *độ dài mã* của mỗi ký hiệu, còn hai bên nén và giải nén cùng tuân theo một quy tắc để tái tạo bảng mã:

1. Sắp các ký hiệu theo **độ dài mã tăng dần**, khi trùng thì theo **mã điểm tăng dần**.
2. Duyệt theo thứ tự đó, gán các số nguyên liên tiếp `0, 1, 2, ...`; khi độ dài tăng từ `L` sang `L'` thì **dịch số sang trái `L' - L` bit**.
3. Mã của ký hiệu là biểu diễn nhị phân của số đó, viết đủ `L'` bit.

Áp dụng cho ví dụ ở mục 1.3 (sắp theo độ dài rồi theo mã điểm: A len 1, B len 2, C len 2):

| Ký tự | Độ dài | Số được gán | Mã |
|---|---|---|---|
| A | 1 | 0 | `0` |
| B | 2 | 1 | `01` |
| C | 2 | 2 | `10` |

Kết quả là bảng mã vẫn prefix-free và có **đúng độ dài tối ưu** của cây Huffman (A dài 1 bit, B và C dài 2 bit — y hệt cây), nhưng phần đầu tệp chỉ tốn ~3 byte/ký hiệu thay vì ~10 byte như cách lưu trực tiếp chuỗi mã.

**Cấu trúc tệp `.huff`:**

| Thành phần | Kích thước | Nội dung |
|---|---|---|
| Magic | 4 byte | `b"HUFF"` — chống ghi nhầm tệp |
| version | 1 byte | số phiên bản định dạng |
| n_symbols | 2 byte | số ký hiệu phân biệt `n` |
| pad | 1 byte | số bit đệm cuối payload (0..7) |
| Bảng ký hiệu | ~3 byte/ký hiệu | độ dài ký tự UTF-8 (1b) + ký tự + độ dài mã (1b), sắp theo mã điểm tăng dần |
| payload | thay đổi | chuỗi bit đã đóng gói thành byte (đệm 0 ở cuối) |

**Các trường hợp biên được xử lý:**

| Trường hợp | Cách xử lý |
|---|---|
| Chỉ một ký hiệu duy nhất | Cây chỉ có 1 nút, gán mã cố định `"0"` (không để mã rỗng) |
| Tệp rỗng | Không có ký hiệu để nén, header ghi `n = 0`, payload rỗng |
| Số bit không chia hết cho 8 | Ghi số bit đệm `pad` vào header để giải nén biết chỗ nào là padding |
| Tệp `.huff` không hợp lệ | Kiểm tra magic và version → báo lỗi rõ ràng thay vì crash |
| Dòng mới trên Windows | Mở/ghi tệp với `newline=""` để không bị đổi `\n` thành `\r\n` |

---

## 2. Tính toán các giá trị O, Ω, Θ

Ký hiệu: `N` = tổng số ký tự của tệp, `n` = số ký hiệu phân biệt, `L` = độ dài mã trung bình (bit/ký tự).

### 2.1. Phân tích từng bước

| Bước | Thời gian | Giải thích |
|---|---|---|
| Đọc tệp + đếm tần suất (`Counter` dùng bảng băm) | **Θ(N)** | phải duyệt qua N ký tự |
| `heapq.heapify` (dựng Min-Heap từ n nút) | **Θ(n)** | heapify của Floyd chạy O(n), *không phải* O(n log n) |
| (n−1) lần `heappop` × 2 + `heappush` | **Θ(n log n)** | mỗi thao tác O(log n), tổng cộng (n−1) lần |
| Duyệt cây lấy độ dài mã (DFS) | **Θ(n)** | duyệt hết n lá, mỗi lá một độ dài |
| Sắp xếp + tái tạo mã canonical | **Θ(n log n)** | sắp n ký hiệu theo (độ dài, mã điểm) |
| Mã hóa N ký tự | **Θ(N·L)** | tổng số bit ghi ra = Σ len(code[ch]) = N·L |
| Đóng gói bit thành byte + ghi/đọc tệp | **Θ(N·L)** | quét từng bit một lần |

Vì bảng mã là prefix-code nên **L ≤ log₂ n** (tính chất của cây Huffman với trọng số tần suất), suy ra `Θ(N·L) = Θ(N log n)`.

### 2.2. Tổng hợp

Tổng thời gian:

```
T(N, n) = Θ(N) + Θ(n log n) + Θ(N log n) = Θ(N + n log n)
```

Do đó:

- **O(N + n log n)** — cận trên.
- **Ω(N)** — cận dưới: bất kỳ thuật toán nén nào cũng phải đọc qua N ký tự để xác định được tần suất, nên không thể chạy nhanh hơn tuyến tính.
- **Θ(N + n log n)** — cận chặt trong trường hợp tổng quát, khi N và n thay đổi độc lập (ví dụ n = Θ(N)).

### 2.3. Trong trường hợp thực tế của bài toán

Tập ký hiệu là mã điểm Unicode nên `n` có trần cố định (1 114 112 mã điểm), và trong văn bản thực tế `n` chỉ khoảng 30–95 (đo được 94 với tiếng Việt, 44 với tiếng Anh) — hằng số rất nhỏ so với N. Khi đó `n log n` là hằng số và:

```
T(N) = Θ(N + n log n) = Θ(N)
```

**Kết luận:** `O(N + n log n)`, `Ω(N)`, và `Θ(N)` khi xem `n` là hằng số — tức là **tiệm cận tuyến tính theo độ dài tệp**. Đây là tính chất tốt nhất có thể, vì bắt buộc phải đọc hết tệp.

### 2.4. Độ phức tạp bộ nhớ

| Thành phần | Bộ nhớ |
|---|---|
| Cây Huffman | `2n − 1` nút ⇒ **O(n)** nút |
| Bảng độ dài mã | **O(n)** |
| Bảng mã tái tạo (n chuỗi bit) | **O(n log n)** bit |
| Chuỗi `text` nạp vào RAM | **O(N)** ký tự — do cách đọc tệp một lần |

Tổng: **O(N + n log n)** theo cách hiện tại. Phần phụ thuộc `N` đến từ cách đọc toàn bộ tệp vào bộ nhớ một lần để đếm tần suất; bản thân thuật toán dựng cây chỉ cần O(n) bộ nhớ.

---

## 3. Đánh giá độ phức tạp thuật toán

### 3.1. Kết quả thực nghiệm

Các lệnh dùng để đo:

```bash
python make_samples.py                                 # sinh tệp văn bản mẫu
python huffman_coder.py demo                           # nén + xác minh round-trip
python huffman_coder.py info samples/sample_vi.txt     # bảng mã + entropy
```

| Tệp mẫu | Đặc điểm | Kích thước gốc | Kích thước nén | Tỷ lệ nén | n ký hiệu | Round-trip |
|---|---|---|---|---|---|---|
| `sample_vi.txt` | Tiếng Việt có dấu | 25 647 B | 12 272 B | **52,15%** | 94 | MATCH |
| `sample_en.txt` | Tiếng Anh | 24 016 B | 13 196 B | **45,05%** | 44 | MATCH |
| `sample_skewed.txt` | Phân bố lệch (1 ký tự ~70%) | 12 079 B | 2 358 B | **80,48%** | 27 | MATCH |

Công thức tỷ lệ nén:

```
Tỷ lệ nén (%) = (1 − S_nén / S_gốc) × 100%
```

**Lưu ý về kích thước tệp mẫu.** Huffman có một chi phí cố định là bảng mã (~3 byte/ký hiệu, không phụ thuộc độ dài tệp). Trên tệp chỉ 2 KB, bảng mã chiếm gần một nửa dung lượng nên tỷ lệ nén bị bóp méo xuống còn 5–20% — đó không phản ánh hiệu quả thuật toán mà phản ánh chi phí khởi tạo. Vì vậy chương trình sinh tệp mẫu khoảng 24 KB cho hai tệp văn bản tự nhiên; khi đó chi phí bảng mã được phân bổ và tỷ lệ nén phản ánh đúng hiệu quả thực tế.

### 3.2. Phân tích entropy và độ dài mã

Với `sample_vi.txt` có 19 080 ký tự, lệnh `info` cho ra:

| Đại lượng | Giá trị |
|---|---|
| Số ký hiệu phân biệt `n` | 94 |
| Entropy `H` (cận dưới lý tưởng) | **4,9464 bit/ký tự** |
| Độ dài mã trung bình `L` (Huffman) | **4,9839 bit/ký tự** |
| Chênh lệch `L − H` | **0,0375 bit/ký tự** |
| Tổng số bit dữ liệu | 95 092 bit (≈ 11 887 byte) |
| Tổng số bit nếu dùng mã cố định 8 bit | 152 640 bit (≈ 19 080 byte) |

Chênh lệch chỉ **0,0375 bit/ký tự** — tức mã Huffman đạt gần đúng cận lý tưởng của bài toán mã hóa ký hiệu theo ký hiệu. Theo định lý Shannon thì `H ≤ L < H + 1` khi `n` là lũy thừa của 2, và `H ≤ L < H + 2` nói chung. Đây là lý do Huffman là mã tối ưu theo nghĩa **trung bình ký hiệu**.

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

Dấu cách (tần suất cao nhất) chỉ tốn 2 bit, còn ký tự hiếm như `ế` tốn tới 8 bit — mã được phân bổ theo xác suất chứ không đồng đều, đúng tinh thần của Huffman.

### 3.3. Nhận xét

**a) Tỷ lệ nén phụ thuộc phân bố tần suất chứ không phụ thuộc độ dài tệp.** `sample_skewed.txt` đạt 80,48% vì tần suất tập trung mạnh vào một ký tự; `sample_vi.txt` đạt 52,15%; `sample_en.txt` chỉ 45,05% vì bảng chữ cái Latin phân bố đều hơn, nhiều nguyên âm có tần suất gần bằng nhau. Đây là đặc tính cơ bản của Huffman: **tần suất càng lệch thì nén càng hiệu quả**.

**b) Huffman vượt trội mã cố định (Fixed-length Code).** Với `sample_vi.txt` có 94 ký hiệu phân biệt, mã cố định cần 7 bit/ký tự cho mọi ký tự (⌈log₂94⌉ = 7), tức 133 560 bit. Huffman chỉ dùng 95 092 bit, tiết kiệm **28,8%** so với mã cố định và **37,7%** so với mã 8 bit/ký tự. Chênh lệch này càng lớn khi phân bố tần suất càng lệch.

**c) Giới hạn của Huffman đơn thuần.** Bảng mã phải được truyền kèm dữ liệu nên với tệp rất nhỏ (vài chữ) tổng dung lượng có thể lớn hơn tệp gốc. Trong bài này đã xử lý bằng mã canonical (~3 byte/ký hiệu thay vì ~10) và bằng cách dùng tệp mẫu đủ lớn.

### 3.4. Kiểm chứng tính đúng đắn

Bộ kiểm thử nội tại (`python huffman_coder.py test`) gồm 11 mục kiểm tra, tất cả đều PASS:

- 6 trường hợp chuỗi (chỉ 1 ký tự, ký tự lặp lại, chuỗi kinh điển, tiếng Việt có dấu, đủ bộ ký tự tiếng Việt, từ lặp nhiều) — với mỗi trường hợp kiểm tra tính **prefix-free** của bảng mã và **round-trip**.
- Tái tạo mã canonical từ bảng độ dài; điều kiện Kraft `Σ 2^(−len) ≤ 1` cho mọi cây Huffman; canonical giữ nguyên độ dài mã gốc.
- Round-trip trên tệp thật với so sánh **byte-for-byte**; xử lý tệp rỗng.

Lệnh `compress` cũng tự giải nén ngay sau khi nén và in kết quả `ROUND-TRIP: MATCH`, nhờ đó mỗi lần chạy đều được kiểm chứng tự động. Bộ kiểm thử này đã phát hiện được hai lỗi mà chạy bình thường không thấy: bảng mã bị lưu ngược hướng khi đọc từ tệp (khiến file giải nén ra rỗng), và Windows tự đổi `\n` thành `\r\n` khi đọc/ghi tệp ở chế độ text — hai lỗi này đều không gây ra lỗi runtime mà chỉ làm sai dữ liệu, nên chỉ kiểm thử round-trip mới bắt được.

BÀI KIỂM TRA GIỮA KỲ — MÔN THUẬT TOÁN NÂNG CAO

Họ và tên: Nguyễn Minh Sáng        

Lớp: 34CNTT11

Đề: Câu 1 — Vận dụng kiến thức Huffman Codes và Data Compression, thực
hiện nén dữ liệu cho tệp văn bản.

Phương án: tệp văn bản (.txt), ngôn ngữ Python.

Mã nguồn: https://github.com/nguyenminhsang2003/Thuat-toan-nang-cao


1. TRÌNH BÀY THUẬT TOÁN

1.1. Nguyên lý.

Thuật toán Huffman nén dữ liệu không mất thông tin (lossless) theo nguyên tắc:
ký hiệu xuất hiện càng nhiều trong văn bản thì mã càng ngắn. Có thể dựng một
cây nhị phân, mỗi lá là một ký tự của tệp, đường đi từ gốc đến lá đó chính là
mã của ký tự (rẽ trái = 0, rẽ phải = 1). Bảng mã sinh ra phải có tính chất
tiền tố (prefix-free) — không mã nào là tiền tố của mã khác — thì khi đọc
chuỗi bit từ trái sang phải sẽ biết chắc chắn ký tự tương ứng, không có khả
năng nhập nhằng.

Phương án thực hiện là nén ở mức ký tự Unicode chứ không phải byte thô. Chữ
có dấu tiếng Việt như "ế" chiếm 2 byte trong UTF-8; nếu nén ở mức byte thì
mỗi chữ bị tách thành 2 ký hiệu riêng biệt, số ký hiệu phân biệt nhiều hơn
và tần suất phân tán hơn, nên độ dài mã trung bình cao hơn. Ở mức ký tự, tệp
tiếng Việt mẫu chỉ có 94 ký hiệu phân biệt (đo ở mục 3.1) và tỷ lệ nén đo
được là 52,15%.


1.2. Thuật toán nén gồm 4 bước.

Bước 1 — Đếm tần suất.
Đọc tệp .txt (UTF-8) thành chuỗi ký tự, đếm số lần xuất hiện của từng ký tự.
Thời gian Θ(N).

Bước 2 — Dựng Min-Heap và cây Huffman.
Đưa các ký hiệu kèm tần suất vào một Min-Heap. Lặp n−1 lần: lấy ra hai nút
nhẹ nhất trong heap, gộp thành một nút mới có trọng số bằng tổng hai trọng
số, rồi đưa nút mới trở lại heap. Khi heap chỉ còn một nút thì đó là gốc cây
Huffman (cây có 2n−1 nút).

Bước 3 — Tạo bảng mã.
Duyệt cây từ gốc xuống lá, mỗi lần rẽ nhánh thì độ dài mã tăng 1. Từ bảng độ
dài đó dựng bảng mã theo quy tắc mã canonical (mục 1.4). Kết quả là bảng mã
prefix-free.

Bước 4 — Ghi bit ra tệp.
Thay từng ký tự trong văn bản bằng mã của nó, gom chuỗi bit thành byte
(8 bit một byte, phần bit cuối đệm 0), rồi ghi xuống tệp .huff: phần đầu
chứa bảng mã và số bit đệm, phần sau là dữ liệu đã nén.

Vì sao dùng Min-Heap: thuật toán cần liên tục tìm hai nút có trọng số nhỏ
nhất. Nếu dò từng nút một thì mỗi lần gộp tốn O(n), cả n−1 lần gộp là O(n²).
Min-Heap lấy ra phần tử nhỏ nhất trong O(log n), nên toàn bộ quá trình gộp
chỉ mất O(n log n).


1.3. Ví dụ minh họa.

Xét chuỗi A B B A C A, tần suất: A = 3, B = 2, C = 1.

Gộp lần 1: hai nút nhẹ nhất C(1) và B(2) gộp thành CB(3).
Gộp lần 2: hai nút nhẹ nhất CB(3) và A(3) gộp thành root(6).

              root (6)
             /          \
          A(3)          CB(3)
                      /      \
                   B(2)    C(1)

Ký tự    Tần suất    Mã    Độ dài
A        3           0     1
B        2           10    2
C        1           11    2

Chuỗi gốc mã hóa thành 0 10 10 0 11 0 = 9 bit, trong khi nếu dùng mã cố định
2 bit/ký tự thì cần 12 bit. Ký tự tần suất cao nhất (A) nhận mã ngắn nhất,
ký tự tần suất thấp nhất (C) nhận mã dài nhất — đúng nguyên lý của Huffman.
Lưu ý mã ngắn nhất không bao giờ được để rỗng: kể cả tệp chỉ có một ký tự
thì mã vẫn là "0" (1 bit), nếu để rỗng sẽ không giải mã được.


1.4. Thuật toán giải nén, mã canonical và định dạng tệp.

Giải nén: đọc phần đầu tệp .huff để lấy bảng độ dài mã, tái tạo lại bảng mã
canonical (cùng quy tắc với bên nén nên được đúng bảng mã đã dùng), đọc phần
dữ liệu, bỏ các bit đệm ở cuối, rồi đi từng bit từ trái sang phải: nối bit
vào bộ đệm, mỗi khi bộ đệm khớp trọn vẹn một mã trong bảng thì ghi ký tự
tương ứng và xóa bộ đệm. Nhờ tính prefix-free, mỗi thời điểm có duy nhất
một mã khớp nên giải mã luôn xác định. Vì bảng mã được nhúng sẵn trong tệp
.huff nên quá trình giải nén hoàn toàn độc lập với tệp gốc — chỉ cần tệp
.huff là đủ để khôi phục nội dung.

Mã canonical: nếu lưu thẳng chuỗi mã của từng ký hiệu vào tệp thì mỗi bit
của mã phải tốn một byte, nên phần đầu tệp rất lớn và làm tỷ lệ nén bị hỏng
dù thuật toán hoàn toàn đúng. Vì vậy tệp chỉ lưu độ dài mã của mỗi ký hiệu,
còn hai bên cùng tái tạo bảng mã theo một quy tắc chung:
  - Sắp ký hiệu theo (độ dài mã tăng dần, mã điểm tăng dần).
  - Gán các số nguyên liên tiếp 0, 1, 2, ...; khi độ dài tăng từ L sang L'
    thì dịch số sang trái (L'−L) bit.
  - Mã = biểu diễn nhị phân của số đó, đủ L' bit.
Áp dụng cho ví dụ ở mục 1.3: A (độ dài 1) → 0; B (độ dài 2) → 01; C (độ dài
2) → 10. Độ dài giống hệt bảng theo đường đi (1, 2, 2) và vẫn prefix-free —
khác nhau chỉ ở cách gán số, mà độ dài mới là thứ quyết định số bit dùng để
mã hóa. Vì vậy mỗi ký hiệu chỉ còn tốn 3–4 byte trong phần đầu tệp.

Cấu trúc tệp .huff:
  Magic         4 byte   chuỗi HUFF, chống ghi nhầm tệp
  version       1 byte   số phiên bản định dạng
  n_symbols     2 byte   số ký hiệu phân biệt
  pad           1 byte   số bit đệm cuối dữ liệu (0–7)
  Bảng ký hiệu  thay đổi ký tự + độ dài mã của ký tự đó
  Dữ liệu       thay đổi chuỗi bit nén đóng gói thành byte

Các trường hợp biên được xử lý trong chương trình: chỉ một ký hiệu duy nhất
thì gán mã "0" (không để mã rỗng); tệp rỗng thì phần đầu ghi n = 0, không có
dữ liệu; số bit không chia hết cho 8 thì lưu số bit đệm vào phần đầu tệp;
tệp .huff sai định dạng thì kiểm tra magic và version rồi báo lỗi rõ ràng;
dòng mới trên Windows thì mở/ghi tệp với tham số newline="" để không bị đổi
\n thành \r\n.


2. TÍNH TOÁN CÁC GIÁ TRỊ O, Ω, Θ

Ký hiệu: N = tổng số ký tự của tệp, n = số ký hiệu phân biệt, L = độ dài
mã trung bình tính bằng bit/ký tự.

Bước                              Thời gian
Đọc tệp + đếm tần suất            Θ(N)
Dựng Min-Heap (heapify)          Θ(n)
n−1 lần gộp nút (pop + push)     Θ(n log n)
Duyệt cây lấy độ dài mã          Θ(n)
Sắp xếp + tái tạo mã canonical   Θ(n log n)
Mã hóa N ký tự + đóng gói bit    Θ(N·L)

Giải thích dòng cuối: mã hóa N ký tự sinh ra tổng N·L bit. Theo định lý
Shannon, độ dài mã trung bình của mã Huffman thỏa L < H + 1, trong đó H là
entropy của nguồn, và H ≤ log2 n. Suy ra L = O(log n), nên thời gian mã hóa
là O(N log n).

Tổng thời gian: T(N, n) = Θ(N) + Θ(n log n) + O(N log n) = O(N + n log n)

  O(N + n log n) — cận trên.
  Ω(N) — cận dưới: bất kỳ thuật toán nén nào cũng phải đọc qua N ký tự để
  biết được tần suất, nên không thể chạy nhanh hơn tuyến tính.
  Θ(N + n log n) — cận chặt khi N và n thay đổi độc lập.

Trong trường hợp thực tế của bài toán: tập ký hiệu là mã điểm Unicode nên n
có trần cố định, và trong các tệp mẫu n chỉ bằng 27 (tiếng Anh 44, tiếng Việt
94) — hằng số rất nhỏ so với N. Khi đó n log n là hằng số và T(N) = Θ(N).

Kết luận: O(N + n log n), Ω(N), và Θ(N) khi coi n là hằng số — tức tiệm cận
tuyến tính theo độ dài tệp. Đây là tính chất tốt nhất có thể, vì bắt buộc
phải đọc hết tệp.

Độ phức tạp bộ nhớ: cây Huffman có 2n−1 nút ⇒ O(n); bảng độ dài mã O(n); bảng
mã tái tạo O(n log n) bit; chuỗi văn bản đọc vào RAM chiếm O(N). Tổng
O(N + n log n) — phần phụ thuộc N đến từ cách đọc cả tệp vào bộ nhớ một lần
để đếm tần suất; bản thân thuật toán dựng cây chỉ cần O(n) bộ nhớ.


3. ĐÁNH GIÁ ĐỘ PHỨC TẠP THUẬT TOÁN

3.1. Kết quả nén thực nghiệm.

Các lệnh dùng để đo:
  python make_samples.py          # sinh tệp văn bản mẫu
  python huffman_coder.py demo    # nén và xác minh round-trip
  python huffman_coder.py info samples/sample_vi.txt

Tệp mẫu                Gốc       Nén       Tỷ lệ nén   n    Round-trip
Tiếng Việt có dấu      25647 B   12272 B   52,15%      94   MATCH
Tiếng Anh              24016 B   13196 B   45,05%      44   MATCH
Phân bố tần suất lệch   12079 B   2358 B    80,48%      27   MATCH

Tỷ lệ nén (%) = (1 − S_nén / S_gốc) × 100

Cột Round-trip: sau khi nén, chương trình giải nén ngược lại rồi so sánh
từng byte với tệp gốc — cả 3 tệp đều MATCH, chứng tỏ quá trình nén–giải nén
không làm thay đổi bất kỳ byte nào.

Về kích thước tệp mẫu: Huffman có một chi phí cố định là phần đầu tệp chứa
bảng mã, và chi phí này không phụ thuộc độ dài tệp. Nếu dùng tệp quá nhỏ thì
phần đầu tệp chiếm tỷ lệ lớn, tỷ lệ nén bị bóp méo và không còn phản ánh
đúng hiệu quả của thuật toán. Vì vậy chương trình sinh tệp mẫu khoảng 24 KB
cho hai tệp văn bản tự nhiên, để chi phí bảng mã được phân bổ đều.


3.2. So sánh với entropy và với mã cố định.

Với tệp tiếng Việt (94 ký hiệu, 19080 ký tự), lệnh info cho ra:

Entropy H (cận dưới lý tưởng)              4,9464 bit/ký tự
Độ dài mã trung bình L (Huffman)          4,9839 bit/ký tự
Chênh lệch L − H                           0,0375 bit/ký tự
Tổng số bit dữ liệu                       95092 bit (xấp xỉ 11887 byte)
Tổng số bit nếu dùng mã cố định 8 bit    152640 bit (xấp xỉ 19080 byte)

Entropy H là số bit trung bình nhỏ nhất mà bất kỳ cách mã hóa ký hiệu nào
cũng không thể thấp hơn. Chênh lệch L − H chỉ 0,0375 bit/ký tự — mã Huffman
đạt gần đúng cận lý tưởng, và đúng như định lý Shannon đã khẳng định:
H ≤ L < H + 1 khi n là lũy thừa của 2, H ≤ L < H + 2 nói chung.

Một số dòng trong bảng mã thực tế sinh ra:

Ký tự        Tần suất    Độ dài mã    Mã
(dấu cách)   4119        2            00
n            1787        3            010
h            1333        4            0111
c            913         4            0110
t            872         5            10010
u            441         6            101011
à            317         6            101101
đ            268         6            101110
.            221         7            1100010
ế            104         8            11101010

Dấu cách (tần suất cao nhất) chỉ tốn 2 bit, còn ký tự hiếm như "ế" tốn tới
8 bit — mã được phân bổ theo xác suất chứ không đồng đều, đúng tinh thần của
Huffman.


3.3. Nhận xét.

a) Tỷ lệ nén phụ thuộc mạnh vào phân bố tần suất.
sample_skewed.txt đạt 80,48% vì tần suất tập trung mạnh vào một ký tự;
sample_en.txt chỉ 45,05% vì bảng chữ cái Latin phân bố đều hơn, nhiều nguyên
âm có tần suất gần bằng nhau. Tần suất càng lệch thì nén càng hiệu quả.

b) Huffman vượt trội mã cố định. Với 94 ký hiệu, mã cố định phải dùng 7
bit/ký tự (⌈log2 94⌉ = 7) tức 133560 bit cho tệp trên; Huffman chỉ dùng
95092 bit — tiết kiệm 28,8% so với mã cố định và 37,7% so với mã 8 bit/ký
tự.

c) Giới hạn của Huffman đơn thuần. Bảng mã phải được truyền kèm dữ liệu nên
với tệp rất nhỏ (vài chữ) tổng dung lượng có thể lớn hơn tệp gốc. Trong bài
này đã xử lý bằng mã canonical và bằng cách dùng tệp mẫu đủ lớn.

d) Kiểm chứng tính đúng đắn. Bộ kiểm thử nội tại (python huffman_coder.py
test) gồm 11 mục, tất cả PASS: 6 trường hợp chuỗi (chỉ 1 ký tự, ký tự lặp,
chuỗi kinh điển, tiếng Việt có dấu, đủ bộ ký tự tiếng Việt, từ lặp nhiều)
với kiểm tra tính prefix-free và round-trip; tái tạo mã canonical từ bảng độ
dài; điều kiện Kraft (tổng 2^(−độ dài) ≤ 1) cho mọi cây Huffman; canonical
giữ nguyên độ dài mã gốc; round-trip trên tệp thật so sánh byte-for-byte;
xử lý tệp rỗng. Lệnh compress tự giải nén ngay sau khi nén và in kết quả
ROUND-TRIP: MATCH. Bộ kiểm thử này đã phát hiện hai lỗi mà chạy bình thường
không thấy: bảng mã bị lưu ngược hướng khi đọc từ tệp (khiến file giải nén
ra rỗng), và Windows tự đổi \n thành \r\n khi đọc/ghi tệp ở chế độ text —
cả hai lỗi không gây lỗi runtime mà chỉ làm sai dữ liệu, nên chỉ kiểm thử
round-trip mới bắt được.

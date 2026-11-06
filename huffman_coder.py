#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
huffman_coder.py
================
Huffman Codes & Data Compression — nén/giải nén tệp văn bản.

Đơn vị ký hiệu: MÃ ĐIỂM UNICODE (phương án B).
Tệp đầu vào đọc theo UTF-8, mỗi ký tự (chữ, dấu, khoảng trắng) là 1 ký hiệu.

MÃ HOÁ CANONICAL (Canonical Huffman)
-------------------------------------
Thay vì lưu chuỗi mã của từng ký hiệu vào tệp, ta chỉ lưu ĐỘ DÀI mã
(codelength). Cả bên nén và bên giải nén dùng chung một quy tắc "canonical"
để tái tạo lại đúng bảng mã từ các độ dài đó. Nhờ vậy phần đầu tệp rất gọn
(~3 byte/ký hiệu thay vì ~10 byte), tỷ lệ nén cao hơn đáng kể.

CẤU TRÚC TỆP .huff (tự mô tả, không cần tệp bảng mã riêng):
    "HUFF"        : magic, 4 byte
    version       : uint8  (1 byte) = 2
    n_symbols     : uint16 (2 byte) — số ký hiệu phân biệt
    pad           : uint8  (1 byte) — số bit đệm cuối payload (0..7)
    bảng ký hiệu  : với mỗi ký hiệu (sắp theo mã điểm tăng dần):
                       char_len (1 byte) | char (UTF-8) | code_len (1 byte)
    payload       : chuỗi bit đã đóng gói thành byte (đệm 0 ở cuối)

Cách dùng (từ dòng lệnh):
    python huffman_coder.py compress   du_lieu.txt  ket_qua.huff
    python huffman_coder.py decompress ket_qua.huff  phuc_hoi.txt
    python huffman_coder.py info       du_lieu.txt
    python huffman_coder.py test       # bộ kiểm thử nội tại
    python huffman_coder.py demo       # chạy thử trên các tệp samples/
"""

import heapq
import math
import os
import sys
from collections import Counter

MAGIC = b"HUFF"
VERSION = 2


# ----------------------------------------------------------------------------
# 1. CẤU TRÚC DỮ LIỆU: nút cây Huffman
# ----------------------------------------------------------------------------
class HuffmanNode:
    """Một nút cây Huffman: lá (mang ký tự) hoặc nút trong (mang hai con)."""

    __slots__ = ("char", "freq", "left", "right")

    def __init__(self, char, freq, left=None, right=None):
        self.char = char        # ký tự (None nếu là nút trong)
        self.freq = freq        # tần suất (trọng số) của nút
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.char is not None

    def __repr__(self):
        return "Node(%r, %d)" % (self.char, self.freq) if self.is_leaf() \
            else "Branch(%d)" % self.freq


# ----------------------------------------------------------------------------
# 2. BƯỚC 1 — ĐẾM TẦN SUẤT: Θ(N)
# ----------------------------------------------------------------------------
def count_frequencies(text):
    """Đếm số lần xuất hiện của mỗi ký tự. Θ(N), bộ nhớ O(n)."""
    return Counter(text)


# ----------------------------------------------------------------------------
# 3. BƯỚC 2 — DẬP CÂY BẰNG MIN-HEAP: Θ(n log n)
# ----------------------------------------------------------------------------
def build_tree(freq):
    """
    Từ bảng tần suất, dùng Min-Heap (heapq) lặp n-1 lần gộp 2 nút nhẹ nhất.
    Trả về gốc cây (None nếu input rỗng).

    MẸO: dùng tuple (freq, tiebreak, node) để heapq không phải so sánh
    trực tiếp các HuffmanNode khi tần suất bằng nhau.
    """
    if not freq:
        return None

    # tie-breaker tăng dần để heapq không bao giờ phải so sánh node khi trùng tần suất
    heap = [(f, i, HuffmanNode(ch, f)) for i, (ch, f) in enumerate(freq.items())]
    counter = len(heap)
    heapq.heapify(heap)  # O(n)

    while len(heap) > 1:
        f1, _, left = heapq.heappop(heap)
        f2, _, right = heapq.heappop(heap)
        merged = HuffmanNode(None, f1 + f2, left, right)
        counter += 1
        heapq.heappush(heap, (f1 + f2, counter, merged))  # O(log n)

    return heap[0][2]


# ----------------------------------------------------------------------------
# 4. BƯỚC 3 — ĐỘ DÀI MÃ TỪ CÂY, rồi MÃ CANONICAL
# ----------------------------------------------------------------------------
def get_code_lengths(root):
    """Duyệt cây Huffman gốc → lá, lấy độ dài đường đi của mỗi ký hiệu.
    Trả về dict {ký tự: độ dài mã}. Θ(n)."""
    lengths = {}
    if root is None:
        return lengths
    if root.is_leaf():
        lengths[root.char] = 1
        return lengths

    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        if node.is_leaf():
            lengths[node.char] = depth
        else:
            stack.append((node.left, depth + 1))
            stack.append((node.right, depth + 1))
    return lengths


def canonical_codes(lengths):
    """
    Tái tạo bảng mã CANONICAL từ độ dài mã — quy tắc chuẩn, giống nhau
    ở cả hai đầu nén/giải nén nên không cần lưu mã vào tệp:

      1. Sắp các ký hiệu theo (độ dài mã tăng dần, mã điểm tăng dần).
      2. Duyệt theo thứ tự đó, gán mã số liên tiếp:
            khi độ dài tăng từ L sang L', dịch mã sang trái (L'-L) bit.
      3. Mã của ký hiệu = biểu diễn nhị phân của số đó, đủ L' bit.

    Kết quả là mã PREFIX-FREE và có đúng độ dài tối ưu của cây Huffman.
    """
    ordered = sorted(lengths.items(), key=lambda kv: (kv[1], ord(kv[0])))
    codes = {}
    code = 0
    prev_len = 0
    for ch, length in ordered:
        code <<= (length - prev_len)
        codes[ch] = format(code, "0%db" % length)
        code += 1
        prev_len = length
    return codes


def build_huffman_codes(text):
    """Pipeline đầy đủ: text -> (bảng mã, độ dài mã, tần suất)."""
    freq = count_frequencies(text)
    root = build_tree(freq)
    lengths = get_code_lengths(root)
    codes = canonical_codes(lengths)
    return codes, lengths, freq


# ----------------------------------------------------------------------------
# 5. BƯỚC 4 — ĐÓNG GÓI BIT THÀNH BYTE (Binary Packing)
# ----------------------------------------------------------------------------
def pack_bits(bit_chunks):
    """Gom danh sách chuỗi '0'/'1' thành bytes. Trả về (data, pad)."""
    stream = "".join(bit_chunks)
    pad = (-len(stream)) % 8
    stream += "0" * pad
    out = bytearray()
    for i in range(0, len(stream), 8):
        out.append(int(stream[i:i + 8], 2))
    return bytes(out), pad


def unpack_bits(data, pad):
    """Ngược pack_bits: lấy lại chuỗi bit (bỏ phần đệm)."""
    bits = "".join(format(b, "08b") for b in data)
    return bits[:len(bits) - pad] if pad else bits


def decode_bits(bits, codes):
    """Giải mã: đi qua bit, gặp mã hoàn chỉnh -> phát ký tự. Θ(N).
    `codes` là dict {ký tự: mã}; hàm tự đảo thành {mã: ký tự}."""
    reverse = {v: k for k, v in codes.items()}
    out = []
    buf = []
    for b in bits:
        buf.append(b)
        s = "".join(buf)
        if s in reverse:
            out.append(reverse[s])
            buf.clear()
    return "".join(out)


# ----------------------------------------------------------------------------
# 6. ĐỊNH DẠNG TỆP .huff (viết/đọc)
# ----------------------------------------------------------------------------
def _write_symbol_table(buf, lengths):
    """Viết bảng ký hiệu (chỉ độ dài mã) — sắp theo mã điểm tăng dần."""
    for ch in sorted(lengths, key=ord):
        raw = ch.encode("utf-8")
        buf += bytes([len(raw)]) + raw + bytes([lengths[ch]])


def _read_symbol_table(data, pos, n_symbols):
    """Đọc bảng ký hiệu. Trả về (dict {ký tự: độ dài}, pos_mới)."""
    lengths = {}
    for _ in range(n_symbols):
        char_len = data[pos]
        pos += 1
        ch = data[pos:pos + char_len].decode("utf-8")
        pos += char_len
        lengths[ch] = data[pos]
        pos += 1
    return lengths, pos


# ----------------------------------------------------------------------------
# 7. NÉN / GIẢI NÉN
# ----------------------------------------------------------------------------
def compress_file(in_path, out_path, verbose=True):
    """Nén tệp văn bản in_path -> out_path (.huff).
    Trả về (size_gốc, size_nén, n_ký_hiệu)."""
    # newline="" : KHÔNG dịch thuật dòng mới, giữ nguyên byte ->
    # roundtrip mới đạt SẤT byte-for-byte (không tự biến \n thành \r\n).
    with open(in_path, "r", encoding="utf-8", newline="") as f:
        text = f.read()

    original_size = os.path.getsize(in_path)

    codes, lengths, _ = build_huffman_codes(text)
    if not codes:
        raise ValueError("Tệp rỗng - không có dữ liệu để nén.")

    payload, pad = pack_bits([codes[ch] for ch in text])

    buf = bytearray(MAGIC)
    buf += bytes([VERSION])
    buf += len(codes).to_bytes(2, "big")           # n_symbols (uint16)
    buf += bytes([pad])
    _write_symbol_table(buf, lengths)
    buf += payload

    with open(out_path, "wb") as f:
        f.write(bytes(buf))

    compressed_size = os.path.getsize(out_path)

    if verbose:
        ratio = compression_ratio(original_size, compressed_size)
        print("[%s] -> [%s]" % (in_path, out_path))
        print("  Kích thước gốc : %d bytes" % original_size)
        print("  Kích thước nén : %d bytes" % compressed_size)
        print("  Tỷ lệ nén      : %.2f%%" % ratio)
        print("  Số ký hiệu     : %d" % len(codes))
        print("  Phần đầu tệp   : %d bytes (%.1f%% tệp nén)" %
              (len(buf) - len(payload),
               100.0 * (len(buf) - len(payload)) / compressed_size))

    return original_size, compressed_size, len(codes)


def decompress_file(in_path, out_path, verbose=True):
    """Giải nén tệp .huff -> tệp văn bản (UTF-8)."""
    with open(in_path, "rb") as f:
        data = f.read()

    if data[:4] != MAGIC:
        raise ValueError("Không phải tệp .huff hợp lệ (thiếu magic 'HUFF').")
    version = data[4]
    if version != VERSION:
        raise ValueError("Phiên bản tệp .huff không được hỗ trợ: %d" % version)

    n_symbols = int.from_bytes(data[5:7], "big")
    pad = data[7]
    pos = 8
    lengths, pos = _read_symbol_table(data, pos, n_symbols)
    codes = canonical_codes(lengths)   # tái tạo lại BẢNG MÃ giống hệt bên nén
    payload = data[pos:]

    text = decode_bits(unpack_bits(payload, pad), codes)

    # newline="" : ghi SÁT, không tự đổi \n thành \r\n (Windows)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

    if verbose:
        print("[%s] -> [%s]" % (in_path, out_path))
        print("  Đã khôi phục: %d ký tự" % len(text))

    return text


# ----------------------------------------------------------------------------
# 8. THỐNG KÊ / ĐÁNH GIÁ
# ----------------------------------------------------------------------------
def compression_ratio(original, compressed):
    """Tỷ lệ nén (%) = (1 - S_nén / S_gốc) * 100."""
    return 0.0 if original == 0 else (1 - compressed / original) * 100


def entropy(freq, total):
    """Entropy H = -Σ p_i log2 p_i (bit/ký tự) — cận dưới lý tưởng."""
    if total == 0:
        return 0.0
    h = 0.0
    for f in freq.values():
        p = f / total
        h -= p * math.log2(p)
    return h


def verify_roundtrip(orig_path, huff_path):
    """Giải nén .huff ra tệp tạm rồi so SẤT VỚI GỐC byte-for-byte."""
    tmp = huff_path + ".check"
    try:
        decompress_file(huff_path, tmp, verbose=False)
        a = open(orig_path, "rb").read()
        b = open(tmp, "rb").read()
        return a == b
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def print_info(path):
    """In bảng mã Huffman + thống kê (dùng lấy số liệu cho báo cáo)."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read()

    codes, lengths, freq = build_huffman_codes(text)
    n_chars = len(text)

    H = entropy(freq, n_chars)
    avg = sum(len(codes[ch]) * freq[ch] for ch in codes) / n_chars \
        if n_chars else 0.0
    total_bits = sum(len(codes[ch]) * freq[ch] for ch in codes)

    print("Tệp          : %s" % path)
    print("Kích thước   : %d bytes (UTF-8), %d ký tự" %
          (os.path.getsize(path), n_chars))
    print("Số ký hiệu   : %d" % len(codes))
    print("Entropy H    : %.4f bit/ký tự (cận lý tưởng)" % H)
    print("Độ dài mã TT : %.4f bit/ký tự (Huffman)" % avg)
    print("             : chênh lệch %.4f bit/ký tự" % (avg - H))
    print("Tổng số bit  : %d  (mã cố định 8 bit/ký tự: %d)"
          % (total_bits, n_chars * 8))
    print()
    print("%-8s %10s %10s  %s" % ("Ký tự", "Tần suất", "Độ dài mã", "Mã"))
    print("-" * 52)
    for ch in sorted(codes, key=lambda c: (-freq[c], c)):
        label = ch if ch not in (" ", "\n", "\t") else repr(ch)
        print("%-8s %10d %10d  %s" % (label, freq[ch], len(codes[ch]), codes[ch]))


# ----------------------------------------------------------------------------
# 9. BỘ KIỂM THỬ NỘI TAI (python huffman_coder.py test)
# ----------------------------------------------------------------------------
def self_test():
    print("=== BÔ KIỂM THỬ ===")
    ok = True

    # (9.1) Kiểm tra prefix-free + roundtrip trên chuỗi nội tại
    cases = [
        ("a", "chỉ 1 ký tự"),
        ("aaaa", "1 ký tự lặp lại"),
        ("abracadabra", "chuỗi kinh điển"),
        ("Xin chào Việt Nam! \nThảo nguyên", "tiếng Việt có dấu + xuống dòng"),
        ("àáâãèéêìíòôõùúđ", "đủ các ký tự tiếng Việt"),
        ("thủy lợi thủy lợi thủy lợi ", "từ lặp nhiều"),
    ]
    for text, desc in cases:
        codes, _, _ = build_huffman_codes(text)
        all_codes = list(codes.values())
        prefix_free = all(
            not (c1 != c2 and c2.startswith(c1))
            for c1 in all_codes for c2 in all_codes)
        packed, pad = pack_bits([codes[ch] for ch in text])
        roundtrip = decode_bits(unpack_bits(packed, pad), codes) == text
        status = prefix_free and roundtrip
        ok &= status
        print("  [%s] %-30s prefix_free=%-5s roundtrip=%s" %
              ("PASS" if status else "FAIL", desc, prefix_free, roundtrip))

    # (9.1b) Canonical phải TÁI TẠO ĐÚNG bảng mã từ chỉ độ dài
    # Bộ độ dài phải thỏa điều kiện Kraft (<= 1) thì mã mới prefix-free.
    lengths = {"a": 1, "b": 2, "c": 3, "d": 3}   # 1/2+1/4+1/8+1/8 = 1
    rebuilt = canonical_codes(lengths)
    canon_ok = (rebuilt == canonical_codes(lengths)) and \
        all(not (c1 != c2 and c2.startswith(c1))
            for c1 in rebuilt.values() for c2 in rebuilt.values()) and \
        all(len(c) == lengths[ch] for ch, c in rebuilt.items())
    ok &= canon_ok
    print("  [%s] %-34s tái tạo mã canonical từ độ dài" %
          ("PASS" if canon_ok else "FAIL", "canonical"))

    # (9.1c) Độ dài mã lấy từ cây Huffman luôn thỏa điều kiện Kraft
    kraft_ok = True
    for text, _ in cases:
        ls = get_code_lengths(build_tree(count_frequencies(text)))
        s = sum(2.0 ** -L for L in ls.values())
        kraft_ok &= (s <= 1.0 + 1e-9)
    ok &= kraft_ok
    print("  [%s] %-34s điều kiện Kraft <= 1 cho mọi cây Huffman" %
          ("PASS" if kraft_ok else "FAIL", "kraft"))

    # (9.1d) Canonical cho ra CÙNG độ dài mã với bảng mã gốc từ cây
    same_len = True
    for text, _ in cases:
        ls = get_code_lengths(build_tree(count_frequencies(text)))
        cc = canonical_codes(ls)
        same_len &= all(len(cc[ch]) == L for ch, L in ls.items())
    ok &= same_len
    print("  [%s] %-34s canonical giữ nguyên độ dài mã gốc" %
          ("PASS" if same_len else "FAIL", "do dai ma"))

    # (9.2) Roundtrip trên tệp thật, so sánh byte-for-byte
    import tempfile
    payload = ("Huffman " * 50 + "Thủy lợi " * 50 + "xã ấp " * 30)
    d = tempfile.mkdtemp()
    p_txt, p_huff = os.path.join(d, "t.txt"), os.path.join(d, "t.huff")
    with open(p_txt, "w", encoding="utf-8", newline="") as f:
        f.write(payload)
    compress_file(p_txt, p_huff, verbose=False)
    match = verify_roundtrip(p_txt, p_huff)
    ok &= match
    print("  [%s] roundtrip tệp thật (byte-for-byte)" %
          ("PASS" if match else "FAIL"))
    if not match:
        a = open(p_txt, "rb").read()
        decompress_file(p_huff, p_txt + ".chk", verbose=False)
        b = open(p_txt + ".chk", "rb").read()
        i = 0
        while i < len(a) and i < len(b) and a[i] == b[i]:
            i += 1
        print("         lệch từ byte %d: gốc=%r khác=%r (chênh độ dài: %d)" %
              (i, a[i] if i < len(a) else None,
               b[i] if i < len(b) else None, len(a) - len(b)))
        os.remove(p_txt + ".chk")

    # (9.3) Tệp rỗng
    p_e = os.path.join(d, "e.txt")
    open(p_e, "w", encoding="utf-8").close()
    p_eh = os.path.join(d, "e.huff")
    try:
        compress_file(p_e, p_eh, verbose=False)
        got = decompress_file(p_eh, os.path.join(d, "e_out.txt"), verbose=False)
        empty_ok = (got == "")
    except ValueError:
        empty_ok = True  # chấp nhận cả việc từ chối nén tệp rỗng
    ok &= empty_ok
    print("  [%s] tệp rỗng được xử lý an toàn" %
          ("PASS" if empty_ok else "FAIL"))
    for p in (p_txt, p_huff, p_e, p_eh):
        if os.path.exists(p):
            os.remove(p)
    try:
        os.rmdir(d)
    except OSError:
        pass

    print("=> KẾT QUẢ: %s" % ("TẤT CẢ PASS" if ok else "CÓ FAIL"))
    return ok


# ----------------------------------------------------------------------------
# 10. DEMO (python huffman_coder.py demo)
# ----------------------------------------------------------------------------
def demo(samples_dir=None):
    """Chạy nén + giải nén + xác minh trên các tệp mẫu trong samples/."""
    base = samples_dir or os.path.join(os.path.dirname(__file__), "samples")
    print("=== DEMO (mặc nguồn: %s) ===" % base)
    any_found = False
    if not os.path.isdir(base):
        print("  Không tìm thấy thư mục samples/ - bỏ qua.")
        return
    for name in sorted(os.listdir(base)):
        if not name.endswith(".txt"):
            continue
        any_found = True
        p = os.path.join(base, name)
        h = p[:-4] + ".huff"
        orig, comp, n = compress_file(p, h, verbose=False)
        match = verify_roundtrip(p, h)
        print("  %-22s nén: %6d -> %6d bytes (%.2f%%), %2d ký hiệu, "
              "roundtrip=%s" %
              (name, orig, comp, compression_ratio(orig, comp), n,
               "MATCH" if match else "MISMATCH"))
    if not any_found:
        print("  Chưa có tệp .txt nào trong samples/.")


# ----------------------------------------------------------------------------
# 11. MAIN / CLI
# ----------------------------------------------------------------------------
def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 0

    cmd = argv[1]

    if cmd == "compress" and len(argv) == 4:
        o, c, n = compress_file(argv[2], argv[3])
        m = verify_roundtrip(argv[2], argv[3])
        print("  ROUND-TRIP: %s" % ("MATCH" if m else "MISMATCH!"))
        return 0 if m else 2

    if cmd == "decompress" and len(argv) == 4:
        decompress_file(argv[2], argv[3])
        return 0

    if cmd == "info" and len(argv) == 3:
        print_info(argv[2])
        return 0

    if cmd == "test":
        return 0 if self_test() else 1

    if cmd == "demo":
        demo(argv[2] if len(argv) > 2 else None)
        return 0

    print("Lệnh không rõ: %r\n" % cmd)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

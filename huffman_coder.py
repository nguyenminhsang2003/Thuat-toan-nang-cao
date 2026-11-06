#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Huffman Codes & Data Compression — nén/giải nén tệp văn bản.

Đơn vị ký hiệu: mã điểm Unicode (mỗi ký tự UTF-8 là 1 ký hiệu).
Dùng mã canonical: tệp chỉ lưu độ dài mã, hai bên cùng tái tạo bảng mã
theo một quy tắc chung.

Cấu trúc tệp .huff:
    "HUFF"       : magic, 4 byte
    version      : uint8 = 2
    n_symbols    : uint16 — số ký hiệu phân biệt
    pad          : uint8 — số bit đệm cuối payload (0..7)
    bảng ký hiệu : char_len (1b) | char (UTF-8) | code_len (1b)
    payload      : chuỗi bit đóng gói thành byte

Cách dùng:
    python huffman_coder.py compress   du_lieu.txt  ket_qua.huff
    python huffman_coder.py decompress ket_qua.huff  phuc_hoi.txt
    python huffman_coder.py info       du_lieu.txt
    python huffman_coder.py test
    python huffman_coder.py demo
"""

import heapq
import math
import os
import sys
import tempfile
from collections import Counter

MAGIC = b"HUFF"
VERSION = 2


# ============================================================================
# CẤU TRÚC DỮ LIỆU
# ============================================================================
class HuffmanNode:
    """Nút cây Huffman: lá (mang ký tự) hoặc nút trong (mang hai con)."""

    __slots__ = ("char", "freq", "left", "right")

    def __init__(self, char, freq, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.char is not None

    def __repr__(self):
        return "Node(%r, %d)" % (self.char, self.freq) if self.is_leaf() \
            else "Branch(%d)" % self.freq


# ============================================================================
# THUẬT TOÁN NÉN
# ============================================================================
def count_frequencies(text):
    """BƯỚC 1: đếm tần suất xuất hiện của mỗi ký tự. Θ(N)."""
    return Counter(text)


def build_tree(freq):
    """BƯỚC 2: dựng cây Huffman bằng Min-Heap. Θ(n log n)."""
    if not freq:
        return None

    # (tần suất, số thứ tự, node) — số thứ tự phá vỡ trường hợp trùng tần suất
    heap = [(f, i, HuffmanNode(ch, f)) for i, (ch, f) in enumerate(freq.items())]
    counter = len(heap)
    heapq.heapify(heap)

    # Gộp hai nút nhẹ nhất cho đến khi chỉ còn một nút (gốc cây)
    while len(heap) > 1:
        f1, _, left = heapq.heappop(heap)
        f2, _, right = heapq.heappop(heap)
        merged = HuffmanNode(None, f1 + f2, left, right)
        counter += 1
        heapq.heappush(heap, (f1 + f2, counter, merged))

    return heap[0][2]


def get_code_lengths(root):
    """BƯỚC 3a: duyệt cây gốc → lá, lấy độ dài mã của mỗi ký hiệu. Θ(n)."""
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
    """BƯỚC 3b: dựng bảng mã canonical từ bảng độ dài mã.

    Quy tắc:
      1. Sắp ký hiệu theo (độ dài mã tăng dần, mã điểm tăng dần).
      2. Gán mã số liên tiếp; khi độ dài tăng từ L sang L' thì dịch mã
         sang trái (L'-L) bit.
      3. Mã = biểu diễn nhị phân của số đó, đủ L' bit.
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
    """Chạy cả 3 bước đầu, trả về (bảng mã, độ dài mã, tần suất)."""
    freq = count_frequencies(text)
    root = build_tree(freq)
    lengths = get_code_lengths(root)
    return canonical_codes(lengths), lengths, freq


# ============================================================================
# ĐÓNG GÓI BIT
# ============================================================================
def pack_bits(bit_chunks):
    """BƯỚC 4a: gom chuỗi '0'/'1' thành bytes. Trả về (data, số bit đệm)."""
    stream = "".join(bit_chunks)
    pad = (-len(stream)) % 8
    stream += "0" * pad
    out = bytearray()
    for i in range(0, len(stream), 8):
        out.append(int(stream[i:i + 8], 2))
    return bytes(out), pad


def unpack_bits(data, pad):
    """Ngược pack_bits, bỏ phần đệm cuối."""
    bits = "".join(format(b, "08b") for b in data)
    return bits[:len(bits) - pad] if pad else bits


def decode_bits(bits, codes):
    """Giải mã chuỗi bit thành văn bản. Θ(N)."""
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


# ============================================================================
# ĐỌC / GHI TỆP .huff
# ============================================================================
def _write_symbol_table(buf, lengths):
    """Ghi bảng ký hiệu (chỉ độ dài mã), sắp theo mã điểm tăng dần."""
    for ch in sorted(lengths, key=ord):
        raw = ch.encode("utf-8")
        buf += bytes([len(raw)]) + raw + bytes([lengths[ch]])


def _read_symbol_table(data, pos, n_symbols):
    """Đọc bảng ký hiệu. Trả về ({ký tự: độ dài}, pos mới)."""
    lengths = {}
    for _ in range(n_symbols):
        char_len = data[pos]
        pos += 1
        ch = data[pos:pos + char_len].decode("utf-8")
        pos += char_len
        lengths[ch] = data[pos]
        pos += 1
    return lengths, pos


def compress_file(in_path, out_path, verbose=True):
    """Nén tệp văn bản. Trả về (size gốc, size nén, số ký hiệu)."""
    with open(in_path, "r", encoding="utf-8", newline="") as f:
        text = f.read()

    original_size = os.path.getsize(in_path)

    codes, lengths, _ = build_huffman_codes(text)
    if not codes:
        raise ValueError("Tệp rỗng - không có dữ liệu để nén.")

    payload, pad = pack_bits([codes[ch] for ch in text])

    # BƯỚC 4b: ghi header rồi ghi payload
    buf = bytearray(MAGIC)
    buf += bytes([VERSION])
    buf += len(codes).to_bytes(2, "big")
    buf += bytes([pad])
    _write_symbol_table(buf, lengths)
    buf += payload

    with open(out_path, "wb") as f:
        f.write(bytes(buf))

    compressed_size = os.path.getsize(out_path)

    if verbose:
        print("[%s] -> [%s]" % (in_path, out_path))
        print("  Kích thước gốc : %d bytes" % original_size)
        print("  Kích thước nén : %d bytes" % compressed_size)
        print("  Tỷ lệ nén      : %.2f%%" %
              compression_ratio(original_size, compressed_size))
        print("  Số ký hiệu     : %d" % len(codes))
        print("  Phần đầu tệp   : %d bytes (%.1f%% tệp nén)" %
              (len(buf) - len(payload),
               100.0 * (len(buf) - len(payload)) / compressed_size))

    return original_size, compressed_size, len(codes)


def decompress_file(in_path, out_path, verbose=True):
    """Giải nén tệp .huff ra tệp văn bản (UTF-8)."""
    with open(in_path, "rb") as f:
        data = f.read()

    if data[:4] != MAGIC:
        raise ValueError("Không phải tệp .huff hợp lệ (thiếu magic 'HUFF').")
    if data[4] != VERSION:
        raise ValueError("Phiên bản tệp .huff không được hỗ trợ: %d" % data[4])

    # Đọc header, tái tạo bảng mã, rồi giải mã payload
    n_symbols = int.from_bytes(data[5:7], "big")
    pad = data[7]
    lengths, pos = _read_symbol_table(data, 8, n_symbols)
    codes = canonical_codes(lengths)

    text = decode_bits(unpack_bits(data[pos:], pad), codes)

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

    if verbose:
        print("[%s] -> [%s]" % (in_path, out_path))
        print("  Đã khôi phục: %d ký tự" % len(text))

    return text


# ============================================================================
# THỐNG KÊ
# ============================================================================
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
    """Giải nén ra tệp tạm rồi so sánh byte-for-byte với tệp gốc."""
    tmp = huff_path + ".check"
    try:
        decompress_file(huff_path, tmp, verbose=False)
        return open(orig_path, "rb").read() == open(tmp, "rb").read()
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def print_info(path):
    """In bảng mã Huffman và các thống kê dùng cho báo cáo."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read()

    codes, _, freq = build_huffman_codes(text)
    n_chars = len(text)

    H = entropy(freq, n_chars)
    total_bits = sum(len(codes[ch]) * freq[ch] for ch in codes)
    avg = total_bits / n_chars if n_chars else 0.0

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


# ============================================================================
# BỘ KIỂM THỬ
# ============================================================================
def self_test():
    """Bộ kiểm thử nội tại: 11 mục, trả về True nếu tất cả PASS."""
    print("=== BÔ KIỂM THỬ ===")
    ok = True

    cases = [
        ("a", "chỉ 1 ký tự"),
        ("aaaa", "1 ký tự lặp lại"),
        ("abracadabra", "chuỗi kinh điển"),
        ("Xin chào Việt Nam! \nThảo nguyên", "tiếng Việt có dấu + xuống dòng"),
        ("àáâãèéêìíòôõùúđ", "đủ các ký tự tiếng Việt"),
        ("thủy lợi thủy lợi thủy lợi ", "từ lặp nhiều"),
    ]

    # Bảng mã phải prefix-free và round-trip được trên mọi chuỗi
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

    # Canonical phải tái tạo đúng bảng mã từ chỉ độ dài
    lengths = {"a": 1, "b": 2, "c": 3, "d": 3}
    rebuilt = canonical_codes(lengths)
    canon_ok = (rebuilt == canonical_codes(lengths)) and \
        all(not (c1 != c2 and c2.startswith(c1))
            for c1 in rebuilt.values() for c2 in rebuilt.values()) and \
        all(len(c) == lengths[ch] for ch, c in rebuilt.items())
    ok &= canon_ok
    print("  [%s] %-34s tái tạo mã canonical từ độ dài" %
          ("PASS" if canon_ok else "FAIL", "canonical"))

    # Độ dài mã lấy từ cây Huffman luôn thỏa điều kiện Kraft
    kraft_ok = True
    for text, _ in cases:
        ls = get_code_lengths(build_tree(count_frequencies(text)))
        kraft_ok &= (sum(2.0 ** -L for L in ls.values()) <= 1.0 + 1e-9)
    ok &= kraft_ok
    print("  [%s] %-34s điều kiện Kraft <= 1 cho mọi cây Huffman" %
          ("PASS" if kraft_ok else "FAIL", "kraft"))

    # Canonical cho ra cùng độ dài mã với bảng mã gốc từ cây
    same_len = True
    for text, _ in cases:
        ls = get_code_lengths(build_tree(count_frequencies(text)))
        cc = canonical_codes(ls)
        same_len &= all(len(cc[ch]) == L for ch, L in ls.items())
    ok &= same_len
    print("  [%s] %-34s canonical giữ nguyên độ dài mã gốc" %
          ("PASS" if same_len else "FAIL", "do dai ma"))

    # Round-trip trên tệp thật, so sánh byte-for-byte
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

    # Tệp rỗng
    p_e, p_eh = os.path.join(d, "e.txt"), os.path.join(d, "e.huff")
    open(p_e, "w", encoding="utf-8").close()
    try:
        compress_file(p_e, p_eh, verbose=False)
        empty_ok = (decompress_file(p_eh, os.path.join(d, "e_out.txt"),
                                    verbose=False) == "")
    except ValueError:
        empty_ok = True
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


# ============================================================================
# DEMO
# ============================================================================
def demo(samples_dir=None):
    """Nén + giải nén + xác minh trên các tệp mẫu trong samples/."""
    base = samples_dir or os.path.join(os.path.dirname(__file__), "samples")
    print("=== DEMO (mặc nguồn: %s) ===" % base)
    if not os.path.isdir(base):
        print("  Không tìm thấy thư mục samples/ - bỏ qua.")
        return

    found = False
    for name in sorted(os.listdir(base)):
        if not name.endswith(".txt"):
            continue
        found = True
        p = os.path.join(base, name)
        h = p[:-4] + ".huff"
        orig, comp, n = compress_file(p, h, verbose=False)
        match = verify_roundtrip(p, h)
        print("  %-22s nén: %6d -> %6d bytes (%.2f%%), %2d ký hiệu, "
              "roundtrip=%s" %
              (name, orig, comp, compression_ratio(orig, comp), n,
               "MATCH" if match else "MISMATCH"))
    if not found:
        print("  Chưa có tệp .txt nào trong samples/.")


# ============================================================================
# CLI
# ============================================================================
def main(argv):
    """Xử lý lệnh dòng lệnh, trả về mã thoát."""
    if len(argv) < 2:
        print(__doc__)
        return 0

    cmd = argv[1]

    if cmd == "compress" and len(argv) == 4:
        compress_file(argv[2], argv[3])
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

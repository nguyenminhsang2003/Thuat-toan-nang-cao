#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_samples.py
===============
Sinh các tệp văn bản mẫu cho thí nghiệm nén Huffman.

Vì sao cần tệp mẫu LỚN?
    Chi phí cố định của Huffman là BẢNG MÃ (~3 byte/ký hiệu). Trên tệp 2 KB,
    bảng mã chiếm phần lớn dung lượng nên tỷ lệ nén bị bóp méo (chỉ 5–20%).
    Trên tệp vài chục KB, chi phí này được phân bổ => tỷ lệ nén phản ánh
    đúng hiệu quả thực tế của thuật toán.

Cách dùng:
    python make_samples.py          # sinh lại toàn bộ tệp mẫu
"""

import os
import random

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")

# --------------------------------------------------------------------------
# Kho câu văn tiếng Việt
# --------------------------------------------------------------------------
VI_SENTENCES = [
    "Công tác thủy lợi là một trong những nội dung trọng tâm trong phát triển kinh tế - xã hội.",
    "Việt Nam có điều kiện khí hậu đặc thù, lượng mưa lớn và tập trung vào mùa mưa.",
    "Mạng lưới kênh mương được tu bổ và kiên cố nhằm đảm bảo khả năng tưới tiêu cho cây trồng.",
    "Các hồ chứa nước đóng vai trò điều tiết dòng chảy và cấp nước sinh hoạt cho người dân.",
    "Đê bao và công trình phòng hộ là những hạng mục không thể thiếu ở vùng đất thấp ven biển.",
    "Nhiều cửa sông lớn chảy qua các tỉnh đồng bằng, đầu nguồn và thường xuyên gây ngập úng.",
    "Việc quản lý, vận hành hồ chứa và đê điều cần có sự phối hợp giữa các cơ quan quản lý.",
    "Nguồn lực tài nguyên nước không phải là vô hạn, vì vậy việc sử dụng hợp lý là yêu cầu cấp thiết.",
    "Tiết kiệm nước trong sản xuất và sinh hoạt giúp giảm đáng kể chi phí cho người dân.",
    "Bảo vệ nguồn nước sạch là trách nhiệm chung của cộng đồng và doanh nghiệp.",
    "Nông nghiệp vẫn chiếm tỷ trọng quan trọng trong tổng sản phẩm quốc gia hàng năm.",
    "Cây lúa, cà phê, hạt điều, chè và thanh long là những sản phẩm xuất khẩu chủ lực.",
    "Ngành du lịch phát triển nhờ vẻ đẹp thiên nhiên, văn hóa đa dạng và nền ẩm thực đặc sắc.",
    "Học tập và nghiên cứu khoa học là nền tảng để nâng cao năng suất lao động.",
    "Người kỹ sư cần biết phân tích dữ liệu và ra quyết định dựa trên bằng chứng cụ thể.",
    "Ứng dụng công nghệ thông tin trong quản lý thủy lợi giúp dự báo chính xác hơn.",
    "Mô hình hồ chứa đa mục tiêu vừa cấp nước, vừa phát điện, vừa phòng hộ.",
    "Chính sách hỗ trợ của nhà nước cho các công trình thủy lợi cần được duy trì bền vững.",
    "Phát triển thủy lợi gắn với phát triển bền vững và ứng phó với biến đổi khí hậu.",
    "Mỗi sinh viên kỹ thuật cần có tinh thần trách nhiệm và làm việc nhóm hiệu quả.",
]

VI_HEADERS = [
    "Về thủy lợi và phát triển bền vững",
    "Quản lý nguồn nước trong bối cảnh mới",
    "Kinh nghiệm vận hành công trình thủy lợi",
    "Thủy lợi và nông nghiệp bền vững",
    "Ứng dụng khoa học trong quản lý nước",
]

# --------------------------------------------------------------------------
# Kho câu tiếng Anh
# --------------------------------------------------------------------------
EN_SENTENCES = [
    "Data compression is the process of encoding information in a more compact form.",
    "Compressed data is typically smaller, faster to transmit, and cheaper to store.",
    "The two main families of compression algorithms are lossless and lossy.",
    "Lossless compression reduces the size of a file without removing any information.",
    "When the file is decompressed, the result is bit for bit identical to the original.",
    "Huffman coding was invented in 1952 by David Huffman, who was a graduate student at MIT.",
    "The central idea is that frequently occurring characters receive short binary codes.",
    "A code table is produced in which no code is a prefix of any other code.",
    "To build the Huffman tree, one begins by counting how often each character appears.",
    "The two least frequent nodes are then combined into a single parent node.",
    "This merging step is repeated until only one node remains, and that node is the root.",
    "A min heap is the natural data structure for this task.",
    "The Huffman code is not always optimal for a single message, since the table must be sent too.",
    "It does guarantee that the average code length is within one bit of the entropy.",
    "This guarantee is what makes the algorithm so useful in practice.",
    "Huffman coding remains a building block inside more complex compressors such as DEFLATE.",
    "Many file formats store a table of code lengths rather than the codes themselves.",
    "This canonical representation is compact and can be reconstructed by both sides.",
    "The reconstruction rule depends only on the lengths, so no extra data is needed.",
    "Modern systems combine Huffman coding with a dictionary based scheme to do even better.",
]

EN_HEADERS = [
    "An introduction to data compression",
    "The Huffman algorithm in practice",
    "Canonical codes and compact file headers",
    "Comparing Huffman with fixed length codes",
    "Limitations and practical considerations",
]


def build_text(sentences, headers, target_bytes, seed):
    """Sinh văn bản nhiều đoạn với cấu trúc câu/đoạn tự nhiên."""
    rnd = random.Random(seed)
    out = []
    size = 0
    while size < target_bytes:
        out.append("")
        out.append(headers[rnd.randrange(len(headers))])
        out.append("")
        for _ in range(rnd.randint(3, 6)):
            out.append(" ".join(sentences[rnd.randrange(len(sentences))]
                                for _ in range(rnd.randint(3, 6))))
            out.append("")
        size = sum(len(line.encode("utf-8")) + 1 for line in out)
    return "\n".join(out).rstrip() + "\n"


def build_skewed(target_bytes):
    """Phân bố tần suất lệch mạnh: 1 ký tự chiếm phần lớn, còn lại rải rác."""
    rnd = random.Random(2024)
    alphabet = "bcdefghijklmnopqrstuvwxyz"
    out = []
    size = 0
    while size < target_bytes:
        line = "a" * rnd.randint(60, 90)
        for _ in range(rnd.randint(5, 12)):
            line += alphabet[rnd.randrange(len(alphabet))]
        out.append(line)
        size += len(line.encode("utf-8")) + 1
    return "\n".join(out) + "\n"


def write(name, content):
    path = os.path.join(BASE, name)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)
    print("  %-24s %7d bytes" % (name, os.path.getsize(path)))


def main():
    os.makedirs(BASE, exist_ok=True)
    print("Sinh tệp mẫu trong: %s" % BASE)
    write("sample_vi.txt", build_text(VI_SENTENCES, VI_HEADERS, 24000, seed=1))
    write("sample_en.txt", build_text(EN_SENTENCES, EN_HEADERS, 24000, seed=2))
    write("sample_skewed.txt", build_skewed(12000))
    print("Xong. Chạy 'python huffman_coder.py demo' để đo tỷ lệ nén.")


if __name__ == "__main__":
    main()

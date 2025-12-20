# -*- coding: utf-8 -*-
"""
Script kiem tra file test.docx co dung format voi cac regex trong app.py khong
"""
import re
from docx import Document

# Regex tu app.py
QUESTION_START_PATTERN = re.compile(
    r"^\s*Question\s*\d+\s*[\.:)\-/]", re.IGNORECASE
)
ANSWER_PATTERN = re.compile(r"Answer\s*:\s*(.+)", re.IGNORECASE)
OPTION_PATTERN = re.compile(r"^\s*([A-D])\s*[\.\)]\s*(.+)", re.IGNORECASE)
GENDER_PATTERN = re.compile(r"(.+)-\s*(woman|man|both)\s*$", re.IGNORECASE)

# Doc file
doc = Document("test.docx")
lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

print("=" * 60)
print("[NOI DUNG FILE test.docx]")
print("=" * 60)
for i, line in enumerate(lines, 1):
    print(f"{i:3}: {line}")

print("\n" + "=" * 60)
print("[PHAN TICH REGEX]")
print("=" * 60)

# Tim cac Question headers
questions_found = []
for i, line in enumerate(lines, 1):
    if QUESTION_START_PATTERN.match(line):
        questions_found.append((i, line))
        print(f"[OK] Line {i}: QUESTION_START_PATTERN matched: '{line[:60]}...'")

print(f"\n>> Tong so Question headers tim duoc: {len(questions_found)}")

# Kiem tra Answer pattern
print("\n--- Kiem tra ANSWER_PATTERN ---")
answers_found = 0
for i, line in enumerate(lines, 1):
    m = ANSWER_PATTERN.search(line)
    if m:
        answers_found += 1
        print(f"[OK] Line {i}: Answer found = '{m.group(1).strip()}'")

print(f">> Tong so Answer: {answers_found}")

# Kiem tra Option pattern (A/B/C/D)
print("\n--- Kiem tra OPTION_PATTERN ---")
options_found = 0
for i, line in enumerate(lines, 1):
    m = OPTION_PATTERN.match(line)
    if m:
        options_found += 1
        print(f"[OK] Line {i}: {m.group(1).upper()}. {m.group(2).strip()[:50]}")

print(f">> Tong so Options: {options_found}")

# Kiem tra Gender pattern (Q15)
print("\n--- Kiem tra GENDER_PATTERN (Q15 - woman/man/both) ---")
gender_found = 0
for i, line in enumerate(lines, 1):
    m = GENDER_PATTERN.match(line)
    if m:
        gender_found += 1
        print(f"[OK] Line {i}: '{m.group(1).strip()[:40]}' -> {m.group(2).lower()}")

print(f">> Tong so Gender items: {gender_found}")

# Tom tat
print("\n" + "=" * 60)
print("[TOM TAT]")
print("=" * 60)
print(f"- Question headers (Q1-Q17):  {len(questions_found)} (can 17)")
print(f"- Answer lines:               {answers_found}")
print(f"- Option lines (A/B/C/D):     {options_found}")
print(f"- Gender items (Q15):         {gender_found} (can 4 cho moi Q15)")

# Kiem tra chi tiet tung Question
print("\n" + "=" * 60)
print("[CHI TIET TUNG QUESTION]")
print("=" * 60)

# Tach thanh cac block theo Question
blocks = []
current_block = []
current_q_num = None

for line in lines:
    if QUESTION_START_PATTERN.match(line):
        if current_block:
            blocks.append((current_q_num, current_block))
        current_block = [line]
        # Lay so Question
        m = re.search(r"Question\s*(\d+)", line, re.IGNORECASE)
        current_q_num = int(m.group(1)) if m else None
    else:
        current_block.append(line)

if current_block:
    blocks.append((current_q_num, current_block))

for q_num, block in blocks:
    print(f"\n--- Question {q_num} ---")
    
    # Xac dinh nhom
    if q_num and 1 <= q_num <= 13:
        print(f"   Nhom: 1 (MCQ don)")
    elif q_num == 14:
        print(f"   Nhom: 2 (Sap xep)")
    elif q_num == 15:
        print(f"   Nhom: 3 (woman/man/both)")
    elif q_num in (16, 17):
        print(f"   Nhom: 4 (MCQ nhieu cau con)")
    
    # Dem cac thanh phan
    opts = sum(1 for l in block if OPTION_PATTERN.match(l))
    ans = sum(1 for l in block if ANSWER_PATTERN.search(l))
    gender = sum(1 for l in block if GENDER_PATTERN.match(l))
    cau_lines = sum(1 for l in block if l.lower().startswith("cau ") or l.lower().startswith(u"câu "))
    
    print(f"   Options: {opts}, Answers: {ans}, Gender items: {gender}, 'Cau X' lines: {cau_lines}")
    
    # Hien thi noi dung
    for l in block[:8]:  # Hien thi toi da 8 dong dau
        preview = l[:70] + "..." if len(l) > 70 else l
        print(f"      {preview}")
    if len(block) > 8:
        print(f"      ... (con {len(block) - 8} dong nua)")

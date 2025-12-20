# -*- coding: utf-8 -*-
"""
Tab Information - Hướng dẫn sử dụng
"""
import streamlit as st


def render_info_tab(tab):
    """Render tab thông tin hướng dẫn"""
    with tab:
        st.subheader("Cấu trúc mỗi Test")
        st.markdown(
            """
**Theo số Question trong file Word:**

- **Q1–13 → Nhóm 1**  
  - Câu trắc nghiệm dạng A/B/C/D  
  - Mỗi câu có dòng `Answer: X` ở cuối  

- **Q14 → Nhóm 2**  
  - Dạng sắp xếp thứ tự  
  - Trong file:  
    ```text
    Question 14:
    Item 1
    Item 2
    Item 3
    Item 4
    ```
  - Không có intro, tất cả các dòng sau `Question 14:` là **các mục cần sắp xếp** theo thứ tự đúng.

- **Q15 → Nhóm 3**  
  - 4 câu con dạng:  
    `Nội dung câu - woman`  
    `Nội dung câu - man`  
    `Nội dung câu - both`  

- **Q16–17 → Nhóm 4**  
  - Mỗi Question gồm 2 câu con:
    ```text
    Question 16:
    (intro nếu có...)
    Câu 1: ...
    A. ...
    B. ...
    C. ...
    Answer: X

    Câu 2: ...
    A. ...
    B. ...
    C. ...
    Answer: Y
    ```

---

### Cấu trúc đề luyện tập (17 câu)

- **Câu 1–13**: 13 câu random từ **Nhóm 1**  
- **Câu 14**: 1 câu từ **Nhóm 2** (dạng sắp xếp)  
- **Câu 15**: 1 block từ **Nhóm 3** (4 câu con woman/man/both)  
- **Câu 16–17**: 2 block từ **Nhóm 4** (mỗi block có 2 câu con trắc nghiệm)  
"""
        )

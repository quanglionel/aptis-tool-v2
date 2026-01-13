# -*- coding: utf-8 -*-
"""
Tool luyện đề APTIS - Entry Point
Ứng dụng Streamlit để luyện đề thi APTIS với 17 câu hỏi
"""
import streamlit as st

# Import các tab
from tabs import (
    render_info_tab,
    render_upload_tab,
    render_stats_tab,
    render_view_tab,
    render_exam_tab,
)
from storage import load_question_bank


# ==========================
#  CẤU HÌNH TRANG
# ==========================

st.set_page_config(page_title="Tool luyện đề từ nhiều Test", layout="wide")

# ---- CSS cho responsive & giao diện gọn gàng ----
CUSTOM_CSS = """
<style>
/* --- Cấu hình chung --- */
.main .block-container {
    max-width: 100%;
    padding-top: 1rem;
    padding-bottom: 3rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

/* Tiêu đề gọn hơn */
h1 { font-size: 1.8rem !important; }
h2 { font-size: 1.5rem !important; }
h3 { font-size: 1.2rem !important; }

/* --- Tối ưu thanh Tabs cho Mobile --- */
.stTabs [role="tablist"] {
    justify-content: flex-start; /* Canh trái để cuộn */
    overflow-x: auto;            /* Cho phép cuộn ngang */
    white-space: nowrap;         /* Không xuống dòng */
    gap: 0.5rem;
    padding-bottom: 5px;
    
    /* Ẩn thanh cuộn nhưng vẫn cuộn được (cho đẹp) */
    scrollbar-width: none; 
    -ms-overflow-style: none;
}
.stTabs [role="tablist"]::-webkit-scrollbar { 
    display: none; 
}

.stTabs [role="tab"] {
    font-size: 0.9rem;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    background-color: #f0f2f6; /* Nền nhẹ cho các tab chưa chọn */
    border: 1px solid #e0e0e0;
}
.stTabs [role="tab"][aria-selected="true"] {
    background-color: #ff4b4b !important; /* Màu nổi bật cho tab đang chọn */
    color: white !important;
    border: none;
}

/* --- Tối ưu các Widget nhập liệu --- */

/* Radio button & Checkbox to hơn để dễ bấm */
.stRadio label, .stCheckbox label {
    font-size: 1rem !important;
    padding-top: 2px;
    padding-bottom: 2px;
}

/* Các nút bấm (Button) full chiều rộng trên mobile */
div.stButton > button {
    width: 100%;
    border-radius: 8px;
    height: 3rem; /* Cao hơn để dễ bấm */
    font-weight: bold;
}

/* Input fields */
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
    min-height: 45px; /* Cao hơn chút */
}

/* --- Responsive Modal/Expander --- */
.streamlit-expanderHeader {
    font-weight: 600;
    font-size: 1rem;
    background-color: #f8f9fa;
    border-radius: 8px;
}

/* Ẩn bớt footer mặc định của Streamlit */
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}

/* --- Mobile Specific Tweaks --- */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
    
    /* Font to hơn chút trên mobile */
    p, li, .stMarkdown {
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==========================
#  SESSION STATE
# ==========================

if "question_bank" not in st.session_state:
    # Tự động tải dữ liệu đã lưu (nếu có)
    st.session_state.question_bank = load_question_bank()
    # Đảm bảo có key 'history' để lưu các câu sai
    if "history" not in st.session_state.question_bank:
        st.session_state.question_bank["history"] = []

if "current_exam" not in st.session_state:
    st.session_state.current_exam = []

if "exam_id" not in st.session_state:
    st.session_state.exam_id = 0


# ==========================
#  MAIN UI
# ==========================

st.title("📚 Tool luyện đề (Phiên bản 2.0 - Multi Upload)")

# Tạo các tab
tab_info, tab_upload, tab_stats, tab_view, tab_exam = st.tabs(
    [
        "ℹ️ Information",
        "1️⃣ Upload Test",
        "2️⃣ Thống kê ngân hàng",
        "3️⃣ Xem / Xóa Test",
        "4️⃣ Tạo đề & Luyện tập",
    ]
)

# Tính counts cho các tab cần dùng
counts = {g: len(st.session_state.question_bank[g]) for g in [1, 2, 3, 4]}

# Render các tab
render_info_tab(tab_info)
render_upload_tab(tab_upload)
render_stats_tab(tab_stats, counts)
render_view_tab(tab_view)
render_exam_tab(tab_exam, counts)

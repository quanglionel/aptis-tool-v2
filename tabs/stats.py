# -*- coding: utf-8 -*-
"""
Tab Stats - Thống kê ngân hàng câu hỏi
"""
import streamlit as st


def render_stats_tab(tab, counts=None):
    """Render tab thống kê ngân hàng"""
    with tab:
        st.header("2️⃣ Thống kê ngân hàng câu hỏi")

        # Luôn tính counts trực tiếp từ session_state để đảm bảo dữ liệu mới nhất
        current_counts = {g: len(st.session_state.question_bank[g]) for g in [1, 2, 3, 4]}

        # Đếm số lượng câu sai trong history
        history_count = len(st.session_state.question_bank.get("history", []))

        st.markdown(
            f"""
- Nhóm 1 (Q1–13, MCQ): **{current_counts[1]}** câu  
- Nhóm 2 (Q14, sắp xếp): **{current_counts[2]}** câu  
- Nhóm 3 (Q15, woman/man/both): **{current_counts[3]}** block  
- Nhóm 4 (Q16–17, multi MCQ): **{current_counts[4]}** block  
---
- **⚠️ Câu làm sai (History): {history_count}** câu
"""
        )

        if history_count > 0:
            if st.button("🗑️ Xóa sạch lịch sử câu sai"):
                st.session_state.question_bank["history"] = []
                from storage import save_question_bank
                save_question_bank(st.session_state.question_bank)
                st.success("Đã xóa sạch lịch sử câu sai!")
                st.rerun()

        with st.expander("🔍 Xem vài ví dụ trong ngân hàng"):
            for g in [1, 2, 3, 4]:
                st.subheader(f"Nhóm {g}")
                sample = st.session_state.question_bank[g][:2]
                if not sample:
                    st.write("Chưa có dữ liệu.")
                else:
                    for q in sample:
                        st.markdown(
                            f"**Test {q['test_id']} – Question {q['index_in_test']} (Nhóm {q['group']})**"
                        )
                        if q["type"] == "mcq":
                            st.text(q["stem"])
                            for lbl, txt in q["options"].items():
                                st.write(f"{lbl}. {txt}")
                            st.write(f"_Answer: {q['answer']}_")
                        elif q["type"] == "mcq_multi":
                            if q["intro"]:
                                st.text(q["intro"])
                            for j, item in enumerate(q["items"], start=1):
                                st.write(f"{j}. {item['stem']}")
                                for lbl, txt in item["options"].items():
                                    st.write(f"   {lbl}. {txt}")
                                st.write(f"   Answer: {item['answer']}")
                        elif q["type"] == "order":
                            st.text(q["prompt"])
                            for j, item in enumerate(q["items"], start=1):
                                st.write(f"{j}. {item}")
                        elif q["type"] == "gender_block":
                            for item in q["items"]:
                                st.write(f"{item['stem']}  →  {item['gender']}")
                        st.markdown("---")

# -*- coding: utf-8 -*-
"""
Tab Exam - Tạo đề và luyện tập (Chế độ mới: Nộp bài mới chấm)
"""
import random
import streamlit as st
from storage import save_question_bank  # Để lưu history

def render_exam_tab(tab, counts=None):
    """Render tab tạo đề và luyện tập"""
    with tab:
        st.header("4️⃣ Tạo đề & Luyện tập")

        # 1. Chọn chế độ
        mode = st.radio(
            "Chọn chế độ:",
            ["🎯 Luyện tập theo Nhóm (Làm hết câu trong kho)", "🎲 Luyện đề Full (Cấu trúc 17 câu)"],
            horizontal=True
        )

        current_counts = {g: len(st.session_state.question_bank.get(g, [])) for g in [1, 2, 3, 4]}

        group_choice = 1
        if mode.startswith("🎯"):
            group_choice = st.selectbox("Chọn nhóm muốn luyện:", [1, 2, 3, 4])
            count = current_counts[group_choice]
            st.info(f"Nhóm {group_choice} hiện có **{count}** câu hỏi.")

        # --- NÚT BẮT ĐẦU ---
        if st.button("🚀 Bắt đầu làm bài", type="primary"):
            exam_questions = []
            
            if mode.startswith("🎯"): # Luyện theo nhóm
                # Lấy TẤT CẢ câu hỏi của nhóm đó
                if current_counts[group_choice] > 0:
                    exam_questions = st.session_state.question_bank[group_choice].copy()
                    # Shuffle thứ tự câu hỏi cho đỡ chán
                    random.shuffle(exam_questions)
                else:
                    st.warning(f"⚠️ Nhóm {group_choice} chưa có dữ liệu!")
            
            else: # Luyện đề Full
                # Kiểm tra đủ câu không
                can_generate = (
                    current_counts[1] >= 13
                    and current_counts[2] >= 1
                    and current_counts[3] >= 1
                    and current_counts[4] >= 2
                )
                if can_generate:
                    q1 = random.sample(st.session_state.question_bank[1], 13)
                    q2 = random.choice(st.session_state.question_bank[2])
                    q3 = random.choice(st.session_state.question_bank[3])
                    q4 = random.sample(st.session_state.question_bank[4], 2)
                    
                    exam_questions.extend(q1)
                    exam_questions.append(q2)
                    exam_questions.append(q3)
                    exam_questions.extend(q4)
                else:
                    st.warning("⚠️ Chưa đủ câu để tạo đề Full 17 câu.")

            if exam_questions:
                # Shuffle items cho câu sắp xếp
                for q in exam_questions:
                        if q["type"] == "order":
                            q["shuffled_items"] = random.sample(q["items"], len(q["items"]))
                
                st.session_state.current_exam = exam_questions
                st.session_state.exam_id += 1
                st.session_state.exam_submitted = False  # Trạng thái chưa nộp bài
                st.success(f"✅ Đã tạo bài luyện tập với {len(exam_questions)} câu hỏi.")
                st.rerun()

        st.markdown("---")

        # --- HIỂN THỊ BÀI LÀM ---
        if st.session_state.get("current_exam"):
            questions = st.session_state.current_exam
            is_submitted = st.session_state.get("exam_submitted", False)
            exam_key = st.session_state.exam_id
            
            # Dictionary lưu đáp án người dùng chọn: { index_in_exam: user_answer_value }
            # Chúng ta dùng session_state để lưu tạm
            if f"user_answers_{exam_key}" not in st.session_state:
                st.session_state[f"user_answers_{exam_key}"] = {}
            
            user_answers = st.session_state[f"user_answers_{exam_key}"]

            # Render từng câu hỏi
            for i, q in enumerate(questions):
                prefix = f"Test {q['test_id']} - Q{q['index_in_test']}"
                st.markdown(f"**Câu {i+1}** ({prefix})")
                
                # --- MCQ ---
                if q["type"] == "mcq":
                    st.write(q["stem"])
                    options = sorted(q["options"].keys())
                    formatted_options = [f"{k}. {q['options'][k]}" for k in options]
                    
                    # Widget select
                    val = st.radio(
                        "Chọn đáp án:", 
                        formatted_options, 
                        key=f"q_{i}_{exam_key}", 
                        index=None,
                        label_visibility="collapsed"
                    )
                    # Lưu đáp án (chỉ lấy A, B, C...)
                    if val:
                        user_answers[i] = val.split(".")[0].strip().upper()

                    # Hiển thị kết quả NẾU đã nộp bài
                    if is_submitted:
                        correct = q["answer"]
                        user_choice = user_answers.get(i)
                        if user_choice == correct:
                            st.success(f"✅ Đúng")
                        else:
                            st.error(f"❌ Sai. Đáp án đúng: {correct}")

                # --- MCQ Multi ---
                elif q["type"] == "mcq_multi":
                    if q.get("intro"): st.write(q["intro"])
                    for j, item in enumerate(q["items"]):
                        st.write(f"_{item['stem']}_")
                        ops = sorted(item["options"].keys())
                        f_ops = [f"{k}. {item['options'][k]}" for k in ops]
                        
                        val = st.radio(
                            "Chọn:", 
                            f_ops, 
                            key=f"q_{i}_{j}_{exam_key}", 
                            index=None,
                            label_visibility="collapsed"
                        )
                        if val:
                            user_answers[f"{i}_{j}"] = val.split(".")[0].strip().upper()
                        
                        if is_submitted:
                            correct = item["answer"]
                            user_choice = user_answers.get(f"{i}_{j}")
                            if user_choice == correct:
                                st.success(f"✅ Đúng")
                            else:
                                st.error(f"❌ Sai. Đáp án đúng: {correct}")

                # --- Order ---
                elif q["type"] == "order":
                    st.write(q["prompt"])
                    # Để đơn giản, phần Order vẫn dùng multiselect logic cũ nhưng không báo đúng sai ngay
                    shuffled = q.get("shuffled_items", q["items"])
                    val = st.multiselect(
                        "Sắp xếp:",
                        shuffled,
                        key=f"q_{i}_{exam_key}"
                    )
                    if val:
                         user_answers[i] = val # List các string
                    
                    if is_submitted:
                        correct = q["items"]
                        user_choice = user_answers.get(i, [])
                        if user_choice == correct:
                            st.success("✅ Đúng thứ tự")
                        else:
                            st.error("❌ Sai thứ tự")
                            with st.expander("Xem đáp án"):
                                for idx, txt in enumerate(correct, 1):
                                    st.write(f"{idx}. {txt}")

                # --- Gender Block ---
                elif q["type"] == "gender_block":
                    for j, item in enumerate(q["items"]):
                        st.write(f"- {item['stem']}")
                        val = st.selectbox(
                            "Người nói:",
                            ["woman", "man", "both"],
                            index=None,
                            key=f"q_{i}_{j}_{exam_key}",
                            placeholder="Chọn..."
                        )
                        if val:
                             user_answers[f"{i}_{j}"] = val.lower()
                        
                        if is_submitted:
                            correct = item["gender"].lower()
                            user_choice = user_answers.get(f"{i}_{j}")
                            if user_choice == correct:
                                st.success("✅ Đúng")
                            else:
                                st.error(f"❌ Sai. Đáp án: {correct}")

                st.markdown("---")

            # --- NÚT NỘP BÀI ---
            if not is_submitted:
                if st.button("📝 Nộp bài & Chấm điểm", type="primary"):
                    st.session_state.exam_submitted = True
                    
                    # Tính điểm & Lưu sai sót
                    total_correct = 0
                    total_questions = 0
                    wrong_entries = []

                    for i, q in enumerate(questions):
                        # Logic chấm điểm
                        if q["type"] == "mcq":
                            total_questions += 1
                            if user_answers.get(i) == q["answer"]:
                                total_correct += 1
                            else:
                                wrong_entries.append(q)
                        
                        elif q["type"] == "mcq_multi":
                            for j, item in enumerate(q["items"]):
                                total_questions += 1
                                if user_answers.get(f"{i}_{j}") == item["answer"]:
                                    total_correct += 1
                                else:
                                    # Lưu cả block nhưng note lại là sai ở item nào thì phức tạp
                                    # Nên ta lưu parent block vào history
                                    if q not in wrong_entries: wrong_entries.append(q)

                        elif q["type"] == "order":
                            total_questions += 1
                            if user_answers.get(i) == q["items"]:
                                total_correct += 1
                            else:
                                wrong_entries.append(q)

                        elif q["type"] == "gender_block":
                            for j, item in enumerate(q["items"]):
                                total_questions += 1
                                if user_answers.get(f"{i}_{j}") == item["gender"].lower():
                                    total_correct += 1
                                else:
                                    if q not in wrong_entries: wrong_entries.append(q)

                    # Lưu vào history (tránh trùng lặp)
                    current_history_ids = {
                        (w["test_id"], w["index_in_test"]) 
                        for w in st.session_state.question_bank.get("history", [])
                    }
                    
                    count_new_wrong = 0
                    for w in wrong_entries:
                        key = (w["test_id"], w["index_in_test"])
                        if key not in current_history_ids:
                            st.session_state.question_bank["history"].append(w)
                            count_new_wrong += 1
                    
                    # Auto save
                    if count_new_wrong > 0:
                        save_question_bank(st.session_state.question_bank)

                    st.toast(f"Đã chấm điểm! Điểm số: {total_correct}/{total_questions}", icon="🎉")
                    if count_new_wrong > 0:
                        st.toast(f"Đã lưu {count_new_wrong} câu sai vào History.", icon="💾")
                    
                    st.rerun()
            
            else:
                st.info("💡 Bạn đã nộp bài. Hãy xem lại kết quả ở trên.")
                if st.button("🔄 Làm bài mới"):
                    st.session_state.current_exam = []
                    st.session_state.exam_submitted = False
                    st.rerun()

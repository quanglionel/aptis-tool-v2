# -*- coding: utf-8 -*-
"""
Tab Upload - Upload nhiều đề thi cùng lúc
"""
import streamlit as st
from parsers import (
    extract_raw_questions_from_docx,
    get_group_for_index,
    parse_group1_mcq,
    parse_order_question,
    parse_gender_block,
    parse_group4_block,
)
from storage import save_question_bank


def process_single_test(uploaded_file, test_id, existing_tests):
    """Xử lý 1 file đề thi và thêm vào ngân hàng"""
    if int(test_id) in existing_tests:
        return False, f"🚫 Test {int(test_id)} đã tồn tại!"
    
    blocks = extract_raw_questions_from_docx(uploaded_file)
    if not blocks:
        return False, f"❌ Test {test_id}: Không tách được Question nào."
    
    added = 0
    for idx, block in enumerate(blocks, start=1):
        if idx > 17:
            break
        
        group = get_group_for_index(idx)
        if group is None:
            continue
        
        # ----- Nhóm 1: MCQ đơn -----
        if group == 1:
            parsed = parse_group1_mcq(block)
            if not parsed:
                continue
            item = parsed
            st.session_state.question_bank[group].append(
                {
                    "type": "mcq",
                    "group": group,
                    "test_id": int(test_id),
                    "index_in_test": idx,
                    "stem": item["stem"],
                    "options": item["options"],
                    "answer": item["answer"],
                }
            )
            added += 1
        
        # ----- Nhóm 2: ORDER -----
        elif group == 2:
            parsed = parse_order_question(block)
            if not parsed:
                continue
            st.session_state.question_bank[group].append(
                {
                    "type": "order",
                    "group": group,
                    "test_id": int(test_id),
                    "index_in_test": idx,
                    "prompt": parsed["prompt"],
                    "items": parsed["items"],
                }
            )
            added += 1
        
        # ----- Nhóm 3: GENDER BLOCK -----
        elif group == 3:
            parsed = parse_gender_block(block)
            if not parsed:
                continue
            st.session_state.question_bank[group].append(
                {
                    "type": "gender_block",
                    "group": group,
                    "test_id": int(test_id),
                    "index_in_test": idx,
                    "items": parsed["items"],
                }
            )
            added += 1
        
        # ----- Nhóm 4: MCQ 1 hoặc nhiều câu con -----
        elif group == 4:
            parsed = parse_group4_block(block)
            if not parsed:
                continue
            
            if parsed["mode"] == "single":
                item = parsed["item"]
                st.session_state.question_bank[group].append(
                    {
                        "type": "mcq",
                        "group": group,
                        "test_id": int(test_id),
                        "index_in_test": idx,
                        "stem": item["stem"],
                        "options": item["options"],
                        "answer": item["answer"],
                    }
                )
            else:  # multi
                st.session_state.question_bank[group].append(
                    {
                        "type": "mcq_multi",
                        "group": group,
                        "test_id": int(test_id),
                        "index_in_test": idx,
                        "intro": parsed["intro"],
                        "items": parsed["items"],
                    }
                )
            added += 1
    
    return True, f"✅ Test {test_id}: Đã thêm {added} câu."


def render_upload_tab(tab):
    """Render tab upload đề thi (Multi-file Support)"""
    with tab:
        st.header("1️⃣ Upload đề thi (Nhiều file cùng lúc)")
        
        # 1. Upload nhiều file
        uploaded_files = st.file_uploader(
            "Chọn các file đề thi (.docx):",
            type=["docx"],
            accept_multiple_files=True,
            help="Bạn có thể chọn nhiều file cùng lúc. Hệ thống sẽ tự động gán mã Test ID."
        )

        if not uploaded_files:
            st.info("👆 Hãy chọn một hoặc nhiều file để bắt đầu.")
            return

        # 2. Xác định Test ID tiếp theo
        # Lấy danh sách ID đã có
        existing_tests = {
            q["test_id"]
            for group in st.session_state.question_bank.values()
            for q in group
        }
        
        next_id = 1
        if existing_tests:
            next_id = max(existing_tests) + 1
        
        st.write("---")
        st.subheader("📋 Danh sách file đã chọn & Mã Test dự kiến")
        
        # 3. Hiển thị danh sách file để review và sửa ID
        upload_data = []
        
        for i, file in enumerate(uploaded_files):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.text(f"📄 {file.name}")
            
            with col2:
                # Tự động gán ID tăng dần: next_id + i
                suggested_id = next_id + i
                
                # Input cho phép sửa ID
                chosen_id = st.number_input(
                    "Test ID:",
                    min_value=1,
                    max_value=999,
                    value=suggested_id,
                    key=f"test_id_input_{i}"
                )
            
            upload_data.append({"file": file, "test_id": chosen_id})
        
        st.write("---")

        # 4. Nút xử lý
        if st.button(f"📥 Xử lý {len(upload_data)} file & Lưu vào ngân hàng", type="primary"):
            results = []
            success_count = 0
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, data in enumerate(upload_data):
                status_text.text(f"Đang xử lý: {data['file'].name} (Test {data['test_id']})...")
                
                # Check trùng ID ngay tại đây (với những ID vừa thêm trong vòng lặp này)
                if int(data["test_id"]) in existing_tests:
                     results.append(f"⚠️ Test {data['test_id']} ({data['file'].name}): Bị bỏ qua vì ID này đã tồn tại!")
                else:
                    success, msg = process_single_test(data["file"], data["test_id"], existing_tests)
                    results.append(f"{'✅' if success else '❌'} {data['file'].name}: {msg}")
                    
                    if success:
                        success_count += 1
                        existing_tests.add(int(data["test_id"]))
                
                progress_bar.progress((idx + 1) / len(upload_data))
            
            status_text.empty()
            progress_bar.empty()
            
            # Hiển thị kết quả
            st.markdown("### 📊 Kết quả chi tiết:")
            for r in results:
                if r.startswith("✅"):
                    st.success(r)
                elif r.startswith("⚠️"):
                    st.warning(r)
                else:
                    st.error(r)
            
            if success_count > 0:
                save_question_bank(st.session_state.question_bank)
                st.success(f"💾 Đã lưu thành công {success_count} đề thi vào hệ thống!")
                st.balloons()

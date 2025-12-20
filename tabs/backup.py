# -*- coding: utf-8 -*-
"""
Tab Backup - Export/Import JSON để lưu trữ dữ liệu
"""
import json
from datetime import datetime
import streamlit as st


def render_backup_tab(tab):
    """Render tab backup/restore"""
    with tab:
        st.header("💾 Backup / Restore ngân hàng câu hỏi")
        
        st.markdown("""
**Lưu ý quan trọng:**
- Dữ liệu trên Streamlit Cloud sẽ **bị mất khi app được cập nhật/redeploy**
- Hãy **Export (tải xuống)** dữ liệu trước khi có thay đổi
- Sau khi app được cập nhật, **Import (tải lên)** file JSON để khôi phục dữ liệu
""")
        
        st.markdown("---")
        
        # ===== EXPORT =====
        st.subheader("📤 Export (Tải xuống)")
        
        # Chuẩn bị dữ liệu export
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "version": "1.0",
            "question_bank": {
                str(k): v for k, v in st.session_state.question_bank.items()
            }
        }
        
        # Tính thống kê
        total_questions = sum(len(v) for v in st.session_state.question_bank.values())
        test_ids = sorted({
            q["test_id"]
            for group in st.session_state.question_bank.values()
            for q in group
        })
        
        st.write(f"**Tổng số câu hỏi trong ngân hàng:** {total_questions}")
        st.write(f"**Các Test đã upload:** {', '.join(map(str, test_ids)) if test_ids else 'Chưa có'}")
        
        if total_questions > 0:
            # Chuyển sang JSON string
            json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
            
            # Tạo tên file với timestamp
            filename = f"aptis_bank_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            st.download_button(
                label="⬇️ Tải xuống file JSON",
                data=json_str,
                file_name=filename,
                mime="application/json",
                type="primary"
            )
        else:
            st.info("Chưa có dữ liệu để export. Hãy upload đề thi trước.")
        
        st.markdown("---")
        
        # ===== IMPORT =====
        st.subheader("📥 Import (Khôi phục)")
        
        st.warning("⚠️ **Lưu ý:** Import sẽ **GHI ĐÈ** toàn bộ dữ liệu hiện tại!")
        
        uploaded_json = st.file_uploader(
            "Chọn file JSON đã export trước đó:",
            type=["json"],
            key="import_json"
        )
        
        if uploaded_json is not None:
            try:
                # Đọc và parse JSON
                content = uploaded_json.read().decode("utf-8")
                import_data = json.loads(content)
                
                # Hiển thị thông tin file
                st.write("**Thông tin file:**")
                st.write(f"- Ngày export: {import_data.get('exported_at', 'Không rõ')}")
                st.write(f"- Version: {import_data.get('version', 'Không rõ')}")
                
                # Đếm số câu
                imported_bank = import_data.get("question_bank", {})
                imported_total = sum(len(v) for v in imported_bank.values())
                imported_tests = sorted({
                    q["test_id"]
                    for group in imported_bank.values()
                    for q in group
                })
                
                st.write(f"- Tổng số câu hỏi: **{imported_total}**")
                st.write(f"- Các Test: {', '.join(map(str, imported_tests)) if imported_tests else 'Không có'}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Xác nhận Import (GHI ĐÈ)", key="confirm_import", type="primary"):
                        # Ghi đè dữ liệu
                        st.session_state.question_bank = {
                            int(k): v for k, v in imported_bank.items()
                        }
                        st.success(f"✅ Đã import thành công {imported_total} câu hỏi từ {len(imported_tests)} Test!")
                        st.rerun()
                
                with col2:
                    if st.button("➕ Thêm vào (KHÔNG ghi đè)", key="merge_import"):
                        # Merge dữ liệu
                        existing_tests = {
                            q["test_id"]
                            for group in st.session_state.question_bank.values()
                            for q in group
                        }
                        
                        added_count = 0
                        skipped_tests = []
                        
                        for group_key, questions in imported_bank.items():
                            group = int(group_key)
                            for q in questions:
                                if q["test_id"] not in existing_tests:
                                    st.session_state.question_bank[group].append(q)
                                    added_count += 1
                                else:
                                    if q["test_id"] not in skipped_tests:
                                        skipped_tests.append(q["test_id"])
                        
                        if added_count > 0:
                            st.success(f"✅ Đã thêm {added_count} câu hỏi mới!")
                        if skipped_tests:
                            st.warning(f"⚠️ Bỏ qua các Test đã tồn tại: {', '.join(map(str, skipped_tests))}")
                        st.rerun()
                        
            except json.JSONDecodeError:
                st.error("❌ File JSON không hợp lệ!")
            except Exception as e:
                st.error(f"❌ Lỗi khi đọc file: {str(e)}")
        
        st.markdown("---")
        
        # ===== CLEAR ALL =====
        st.subheader("🗑️ Xóa toàn bộ dữ liệu")
        
        if st.button("🗑️ Xóa TẤT CẢ ngân hàng câu hỏi", key="clear_all"):
            st.session_state.question_bank = {1: [], 2: [], 3: [], 4: []}
            st.session_state.current_exam = []
            st.success("✅ Đã xóa toàn bộ dữ liệu!")
            st.rerun()

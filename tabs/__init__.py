# -*- coding: utf-8 -*-
"""
Tabs package - Chứa các tab của ứng dụng
"""
from .info import render_info_tab
from .upload import render_upload_tab
from .stats import render_stats_tab
from .view import render_view_tab
from .exam import render_exam_tab
from .backup import render_backup_tab

__all__ = [
    "render_info_tab",
    "render_upload_tab", 
    "render_stats_tab",
    "render_view_tab",
    "render_exam_tab",
    "render_backup_tab",
]

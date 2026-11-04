"""
Module ui: Cung cấp giao diện đồ họa (Tkinter GUI) và giao diện dòng lệnh (CLI)
phục vụ chơi cờ, biểu diễn trực quan và kiểm tra trực tiếp bởi giảng viên.
"""

from .cli import run_cli
from .gui import run_gui

__all__ = ["run_cli", "run_gui"]

"""
Module ui: Cung cấp giao diện đồ họa (Tkinter GUI) và giao diện dòng lệnh (CLI)
phục vụ chơi cờ, biểu diễn trực quan và kiểm tra trực tiếp bởi giảng viên.
"""

from .cli import run_cli

__all__ = ["run_cli", "run_gui"]


def __getattr__(name: str):
    if name == "run_gui":
        from .gui import run_gui
        return run_gui
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

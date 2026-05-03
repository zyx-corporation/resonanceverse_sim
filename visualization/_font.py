"""macOS/Linux両対応の日本語フォント設定"""
import matplotlib
import matplotlib.pyplot as plt


def setup_japanese_font():
    """日本語フォントを自動検出して設定"""
    import matplotlib.font_manager as fm

    candidates = [
        "Hiragino Sans",
        "Hiragino Maru Gothic Pro",
        "Yu Gothic",
        "Noto Sans CJK JP",
        "IPAexGothic",
        "DejaVu Sans",
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            matplotlib.rc("font", family=name)
            return name

    # フォールバック: matplotlib デフォルト
    return "default"


# モジュールインポート時に自動適用
_font_name = setup_japanese_font()

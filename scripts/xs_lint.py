#!/usr/bin/env python3
"""xs_lint — .xs 啟發式驗證（PostToolUse: Write|Edit）。

職責：被編輯檔為 *.xs 時，對「明顯結構問題」與「未知函數 token」提出**非阻斷式**警示。
限制：XS 無公開 grammar / 編譯器，此為啟發式檢查，非完整語法驗證（見 SPEC Out of Scope）。

零第三方相依（Python 3 stdlib only）。一律 exit 0（非阻斷）。
"""
from __future__ import annotations

import json
import re
import sys

# Windows console 預設可能非 UTF-8（cp950），中文警示會 UnicodeEncodeError。
# 防禦性轉 UTF-8（stdlib，3.7+）。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

# ⚠️ 骨架佔位：KNOWN_TOKENS 待蒸餾期由 vscode-xs grammar(xs.tmLanguage.json)的
# keyword/bif/sysfnc/variable/constant 名單生成並嵌入此處（小寫）。
# 在它為空之前，未知函數檢查停用，只跑結構檢查（避免大量誤報）。
KNOWN_TOKENS: frozenset[str] = frozenset()


def read_event() -> dict:
    """從 stdin 讀 PostToolUse 事件 JSON；失敗則回空 dict。"""
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}


def get_target_path(event: dict) -> str | None:
    """取被編輯檔路徑；非 *.xs 回 None。"""
    path = (event.get("tool_input") or {}).get("file_path")
    if isinstance(path, str) and path.lower().endswith(".xs"):
        return path
    return None


def strip_comments(src: str) -> str:
    """移除 XS 註解：區塊 {...}（可巢狀，這裡簡化為非貪婪）與行註解 //。"""
    src = re.sub(r"\{[^{}]*\}", " ", src)  # 區塊註解（簡化，不處理深層巢狀）
    src = re.sub(r"//[^\n]*", " ", src)  # 行註解
    return src


def check_structure(code: str) -> list[str]:
    """結構檢查：begin/end 配對、if 是否缺 then。回警示清單。"""
    warnings: list[str] = []
    lower = code.lower()

    n_begin = len(re.findall(r"\bbegin\b", lower))
    n_end = len(re.findall(r"\bend\b", lower))
    if n_begin != n_end:
        warnings.append(f"begin / end 不成對（begin={n_begin}, end={n_end}）")

    n_if = len(re.findall(r"\bif\b", lower))
    n_then = len(re.findall(r"\bthen\b", lower))
    if n_if > n_then:
        warnings.append(f"有 if 缺對應 then（if={n_if}, then={n_then}）")

    return warnings


def check_unknown_tokens(code: str) -> list[str]:
    """未知函數 token 檢查（依賴 KNOWN_TOKENS；未填則跳過）。"""
    if not KNOWN_TOKENS:
        return []
    warnings: list[str] = []
    # 啟發式：抓 `識別字(` 形式的呼叫名
    for name in {m.lower() for m in re.findall(r"\b([A-Za-z_]\w*)\s*\(", code)}:
        if name not in KNOWN_TOKENS:
            warnings.append(f"未知函數 token：{name}")
    return warnings


def main() -> int:
    event = read_event()
    path = get_target_path(event)
    if path is None:
        return 0  # 非 .xs，靜默

    try:
        with open(path, encoding="utf-8-sig") as f:
            raw = f.read()
    except OSError:
        return 0  # 讀不到就不擾民

    code = strip_comments(raw)
    warnings = check_structure(code) + check_unknown_tokens(code)

    if warnings:
        print(f"⚠️ XS 檢查（{path}）：", file=sys.stderr)
        for w in warnings:
            print(f"  - {w}", file=sys.stderr)
    return 0  # 永遠非阻斷


if __name__ == "__main__":
    sys.exit(main())

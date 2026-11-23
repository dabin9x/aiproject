from pathlib import Path
import ast

p = Path("/mnt/data/03_rent_conversion.py")
src = p.read_text(encoding="utf-8")
print("파일:", p)
print("줄 수:", len(src.splitlines()))
try:
    ast.parse(src)
    print("현재 업로드된 파일: Python 문법 검사 통과")
except SyntaxError as e:
    print("문법 오류:", e.msg, "줄:", e.lineno, "열:", e.offset)
    print(repr(e.text))

# 들여쓰기 위험 요소 확인
tabs = [i for i, line in enumerate(src.splitlines(), 1) if "\t" in line]
print("탭 문자가 포함된 줄:", tabs[:30] if tabs else "없음")

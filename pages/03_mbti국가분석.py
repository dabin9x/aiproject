from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------
# 페이지 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="국가별 MBTI 분석",
    page_icon="🌍",
    layout="wide",
)

MBTI_TYPES = [
    "INFJ", "ISFJ", "INTP", "ISFP",
    "ENTP", "INFP", "ENTJ", "ISTP",
    "INTJ", "ESFP", "ESTJ", "ENFP",
    "ESTP", "ISTJ", "ENFJ", "ESFJ",
]


# ---------------------------------------------------------
# CSV 데이터 불러오기 및 전처리
# ---------------------------------------------------------
@st.cache_data
def load_data(csv_path: str) -> pd.DataFrame:
    """CSV 파일을 읽고 MBTI 비율을 백분율로 변환합니다."""
    try:
        data = pd.read_csv(csv_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        data = pd.read_csv(csv_path, encoding="cp949")

    data.columns = data.columns.astype(str).str.strip()

    required_columns = ["Country"] + MBTI_TYPES
    missing_columns = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "CSV 파일에 필요한 컬럼이 없습니다: "
            + ", ".join(missing_columns)
        )

    data = data[required_columns].copy()
    data["Country"] = data["Country"].astype(str).str.strip()

    for column in MBTI_TYPES:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(subset=required_columns)
    data = data[data["Country"] != ""]

    if data.empty:
        raise ValueError("CSV 파일에 분석할 데이터가 없습니다.")

    # 원본 데이터가 0~1 사이의 소수 비율이면 백분율로 변환
    if data[MBTI_TYPES].max().max() <= 1:
        data[MBTI_TYPES] = data[MBTI_TYPES] * 100

    return data.sort_values("Country").reset_index(drop=True)


# ---------------------------------------------------------
# 페이지 제목
# ---------------------------------------------------------
st.title("🌍 국가별 MBTI 분석")
st.write(
    "국가를 선택하면 해당 국가의 MBTI 16가지 유형별 비율을 "
    "높은 순서대로 확인할 수 있습니다."
)


# ---------------------------------------------------------
# CSV 파일 위치 찾기
# pages 폴더에서 실행되는 경우 프로젝트 최상위 폴더를 먼저 확인
# ---------------------------------------------------------
project_dir = Path(__file__).resolve().parent.parent
csv_path = project_dir / "countriesMBTI_16types.csv"

# 다른 위치에 CSV가 있는 경우를 위한 대체 경로
if not csv_path.exists():
    alternative_paths = [
        Path(__file__).resolve().parent / "countriesMBTI_16types.csv",
        Path.cwd() / "countriesMBTI_16types.csv",
    ]

    for candidate in alternative_paths:
        if candidate.exists():
            csv_path = candidate
            break

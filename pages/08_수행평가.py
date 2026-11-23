from pathlib import Path
import re

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression


# ---------------------------------------------------------
# 지역별 아파트 전월세 전환율 분석
# CSV 파일은 pages 폴더의 한 단계 위에 저장합니다.
# 파일명: temperature.csv 또는 지역별 전월세 전환율_아파트.csv
# ---------------------------------------------------------

st.set_page_config(
    page_title="지역별 아파트 전월세 전환율 분석",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 지역별 아파트 전월세 전환율 분석")
st.write("지역과 연도를 선택해 월별 전월세 전환율을 확인하고 다음 달 전환율을 예측합니다.")


# CSV 파일 찾기
project_dir = Path(__file__).resolve().parent.parent
csv_files = [
    project_dir / "temperature.csv",
    project_dir / "지역별 전월세 전환율_아파트.csv"
]

csv_path = None
for candidate in csv_files:
    if candidate.exists():
        csv_path = candidate
        break

if csv_path is None:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.info(
        "CSV 파일을 pages 폴더의 상위 폴더에 저장해 주세요. "
        "파일명은 temperature.csv 또는 지역별 전월세 전환율_아파트.csv 입니다."
    )
    st.stop()


@st.cache_data
def read_csv_file(file_name):
    """한글 CSV 인코딩을 순서대로 시도합니다."""
    last_error = None

    for encoding in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
        try:
            return pd.read_csv(file_name, encoding=encoding, dtype=str)
        except Exception as error:
            last_error = error

    raise ValueError(f"CSV 파일을 읽을 수 없습니다: {last_error}")


@st.cache_data
def prepare_data(file_name):
    raw = read_csv_file(file_name)

    # 실제 업로드 자료의 지역 열은 지역, 지역.1, 지역.2입니다.
    region_columns = ["지역", "지역.1", "지역.2"]
    for column in region_columns:
        if column not in raw.columns:
            raise ValueError(f"CSV에 '{column}' 열이 없습니다.")

    # 첫 번째 데이터 행은 열 이름 설명(전월세 전환율)이므로 제외합니다.
    raw = raw.iloc[1:].copy()

    month_columns = []
    for column in raw.columns:
        match = re.fullmatch(r"(\d{4})년\s*(\d{1,2})월", str(column).strip())
        if match:
            month_columns.append(column)

    if not month_columns:
        raise ValueError("예: 2026년 1월 형식의 월별 열을 찾을 수 없습니다.")

    records = []

    for _, row in raw.iterrows():
        region_parts = []

        for column in region_columns:
            value = str(row[column]).strip()

            if value and value.lower() != "nan" and value != "-":
                if not region_parts or region_parts[-1] != value:
                    region_parts.append(value)

        if not region_parts:

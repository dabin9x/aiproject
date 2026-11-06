import re
from pathlib import Path

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import MultipleLocator, FuncFormatter


# --------------------------------------------------
# Streamlit 기본 설정
# --------------------------------------------------

st.set_page_config(
    page_title="은평구 연령별 인구 분석",
    page_icon="🌸",
    layout="wide"
)


# --------------------------------------------------
# 한글 폰트 설정
# --------------------------------------------------

def set_korean_font():

    font_paths = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf"
    ]

    for path in font_paths:

        if Path(path).exists():

            font_manager.fontManager.addfont(path)

            font_name = font_manager.FontProperties(
                fname=path
            ).get_name()

            plt.rcParams["font.family"] = font_name
            plt.rcParams["axes.unicode_minus"] = False

            return font_name

    return "sans-serif"


font_name = set_korean_font()


# --------------------------------------------------
# 프로젝트 경로
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = PROJECT_DIR / "population.csv"


# --------------------------------------------------
# CSV 한글 인코딩 자동 처리
# --------------------------------------------------

@st.cache_data
def load_data(file_path):

    encodings = [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]

    last_error = None

    for encoding in encodings:

        try:

            data = pd.read_csv(
                file_path,
                encoding=encoding
            )

            data.columns = (
                data.columns.astype(str).str.strip()
            )

            return data, encoding

        except UnicodeDecodeError as error:

            last_error = error

    raise ValueError(
        "CSV 파일의 한글 인코딩을 확인할 수 없습니다."
    ) from last_error

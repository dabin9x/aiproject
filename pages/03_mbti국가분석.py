
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="국가별 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 세계 국가별 MBTI 분석")
st.markdown("국가를 선택하여 MBTI 16가지 유형의 비율을 분석해 보세요.")

# ==========================================
# 2. MBTI 유형 목록
# ==========================================
MBTI_TYPES = [
    "INFJ", "ISFJ", "INTP", "ISFP",
    "ENTP", "INFP", "ENTJ", "ISTP",
    "INTJ", "ESFP", "ESTJ", "ENFP",
    "ESTP", "ISTJ", "ENFJ", "ESFJ"
]

# ==========================================
# 3. CSV 파일 경로 찾기
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = BASE_DIR / "countriesMBTI_16types.csv"

if not CSV_PATH.exists():
    st.error("CSV 데이터 파일을 찾을 수 없습니다.")
    st.info(
        "countriesMBTI_16types.csv 파일을 "
        "프로젝트 최상위 폴더에 넣어주세요."
    )
    st.stop()

# ==========================================
# 4. 데이터 불러오기
# ==========================================
@st.cache_data
def load_data(path):
    try:
        data = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        data = pd.read_csv(path, encoding="cp949")

    data.columns = data.columns.str.strip()

    required = ["Country"] + MBTI_TYPES

    missing = [
        col for col in required
        if col not in data.columns
    ]

    if missing:
        raise ValueError(
            f"CSV 컬럼이 없습니다: {missing}"
        )

    data = data[required].copy()

    data["Country"] = (
        data["Country"].astype(str).str.strip()
    )

    for col in MBTI_TYPES:
        data[col] = pd.to_numeric(
            data[col], errors="coerce"
        )

    data = data.dropna(subset=required)
    data = data[data["Country"] != ""]

    if data.empty:
        raise ValueError("데이터가 비어 있습니다.")

    # 소수 비율을 백분율로 변환
    if data[MBTI_TYPES].max().max() <= 1:
        data[MBTI_TYPES] = data[MBTI_TYPES] * 100

    return data.sort_values(
        "Country"
    ).reset_index(drop=True)


try:
    df = load_data(str(CSV_PATH))

except Exception as e:
    st.error(f"데이터 로딩 오류: {e}")
    st.stop()

# ==========================================
# 5. 국가 선택
# ==========================================
countries = df["Country"].tolist()

default_index = (
    countries.index("South Korea")
    if "South Korea" in countries
    else 0
)

selected_country = st.selectbox(
    "🌎 분석할 국가를 선택하세요",
    countries,
    index=default_index
)

# ==========================================
# 6. 선택 국가 데이터 추출
# ==========================================
country_data = df[
    df["Country"] == selected_country
]

if country_data.empty:
    st.error("선택한 국가의 데이터가 없습니다.")
    st.stop()

country_row = country_data.iloc[0]

chart_df = pd.DataFrame({
    "MBTI": MBTI_TYPES,
    "비율": [
        float(country_row[mbti])
        for mbti in MBTI_TYPES
    ]
})

# 비율이 높은 순서로 정렬
chart_df = chart_df.sort_values(
    "비율",
    ascending=False
).reset_index(drop=True)

# ==========================================
# 7. 1위 및 2위 분석
# ==========================================
top_type = chart_df.iloc[0]["MBTI"]
top_rate = chart_df.iloc[0]["비율"]

if len(chart_df) >= 2:
    second_type = chart_df.iloc[1]["MBTI"]
    second_rate = chart_df.iloc[1]["비율"]
else:
    second_type = "없음"
    second_rate = 0

# ==========================================
# 8. 핵심 통계 표시
# ==========================================
st.subheader(
    f"📊 {selected_country} MBTI 분석 결과"
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "🥇 가장 높은 MBTI",
    top_type
)

col2.metric(
    "1위 비율",
    f"{top_rate:.2f}%"
)

col3.metric(
    "🥈 2위 MBTI",
    second_type,
    f"{second_rate:.2f}%"
)

st.divider()

# ==========================================
# 9. 그래프 색상 설정
# ==========================================

# 1위는 빨간색
# 나머지는 진한 파랑에서 연한 파랑으로

blue_gradient = [
    "#1769AA",
    "#287FC0",
    "#3D94D2",
    "#55A7DF",
    "#70B8E8",
    "#8BC7EF",
    "#A5D4F3",
    "#B9DFF6",
    "#C8E6F8",
    "#D2EBFA",
    "#DAEFFB",
    "#E1F2FC",
    "#E7F5FD",
    "#ECF7FD",
    "#F1F9FE"
]

bar_colors = (
    ["#E53935"]
    + blue_gradient[:len(chart_df)-1]
)

# ==========================================
# 10. 막대그래프 생성
# ==========================================
fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=chart_df["MBTI"],
        y=chart_df["비율"],

        marker=dict(
            color=bar_colors
        ),

        text=[
            f"{v:.2f}%"
            for v in chart_df["비율"]
        ],

        textposition="outside",

        hovertemplate=(
            "<b>%{x}</b><br>"
            "비율: %{y:.2f}%"
            "<extra></extra>"
        )
    )
)

max_rate = float(chart_df["비율"].max())

fig.update_layout(
    title=f"{selected_country} MBTI 유형별 비율",

    xaxis_title="MBTI 유형",

    yaxis_title="비율 (%)",

    yaxis=dict(
        rangemode="tozero",
        range=[
            0,
            max_rate * 1.2 if max_rate > 0 else 1
        ],
        ticksuffix="%"
    ),

    plot_bgcolor="white",

    paper_bgcolor="white",

    showlegend=False,

    height=550,

    margin=dict(
        l=30,
        r=30,
        t=70,
        b=40
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================
# 11. MBTI 순위표
# ==========================================
st.subheader("🏆 MBTI 유형별 순위")

result_df = chart_df.copy()

result_df.insert(
    0,
    "순위",
    range(1, len(result_df) + 1)
)

result_df["비율"] = result_df["비율"].apply(
    lambda x: f"{x:.2f}%"
)

st.dataframe(
    result_df,
    hide_index=True,
    use_container_width=True
)

# ==========================================
# 12. 데이터 안내
# ==========================================
with st.expander("ℹ️ 데이터 분석 안내"):

    st.write("""
    1. 빨간색은 해당 국가에서 비율이 가장 높은 MBTI입니다.

    2. 나머지 유형은 높은 순서부터
       진한 파란색에서 연한 파란색으로 표시됩니다.

    3. 국가를 변경하면 그래프와 순위가 자동으로 변경됩니다.

    4. 원본 데이터가 소수 형태이면 자동으로 백분율로 변환합니다.

    5. 국가별 비율 합계는 원본 자료의 특성에 따라
       정확히 100%가 아닐 수 있습니다.

    6. 이 자료는 참고용 통계이며 개인이나 국민 전체의
       성격을 단정하는 근거로 사용하면 안 됩니다.
    """)

st.caption(
    "자료: countriesMBTI_16types.csv"
)


from pathlib import Path
import re

import pandas as pd
import streamlit as st
import plotly.graph_objects as go


# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="아파트 전월세 전환율 분석",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 지역별 아파트 전월세 전환율 분석")
st.caption("지역과 연도를 선택하고 선형회귀로 다음 달 전환율을 예측합니다.")


# ==========================================
# 2. CSV 파일 위치 확인
# ==========================================

# 현재 파일은 pages 폴더에 있습니다.
# CSV 파일은 프로젝트 최상위 폴더에 있습니다.

BASE_DIR = Path(__file__).resolve().parent.parent

CSV_FILE = BASE_DIR / "지역별 전월세 전환율_아파트.csv"

# temperature.csv라는 이름을 사용하는 경우도 지원
if not CSV_FILE.exists():
    CSV_FILE = BASE_DIR / "temperature.csv"

if not CSV_FILE.exists():
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.write("현재 검색한 폴더:", str(BASE_DIR))
    st.write("필요한 파일명:")
    st.code(
        "지역별 전월세 전환율_아파트.csv\n"
        "또는\n"
        "temperature.csv"
    )
    st.stop()


# ==========================================
# 3. CSV 데이터 불러오기
# ==========================================

@st.cache_data
def load_data(file_path):

    df = None

    for encoding in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:

        try:
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                dtype=str
            )
            break

        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError("CSV 한글 인코딩을 읽을 수 없습니다.")

    df.columns = [str(c).strip() for c in df.columns]

    region_columns = ["지역", "지역.1", "지역.2"]

    for col in region_columns:
        if col not in df.columns:
            raise ValueError(
                f"CSV에서 {col} 열을 찾을 수 없습니다. "
                "CSV의 열 이름을 확인해 주세요."
            )

    # 월별 데이터 열 찾기
    month_columns = []

    for col in df.columns:

        match = re.fullmatch(
            r"(\d{4})년\s*(\d{1,2})월",
            str(col).strip()
        )

        if match:
            month_columns.append(col)

    if not month_columns:
        raise ValueError(
            "월별 데이터 열을 찾을 수 없습니다. "
            "예: 2026년 1월"
        )

    records = []

    for _, row in df.iterrows():

        region_parts = []

        for col in region_columns:

            value = str(row[col]).strip()

            if (
                value
                and value.lower() != "nan"
                and value != "-"
            ):
                if not region_parts or region_parts[-1] != value:
                    region_parts.append(value)

        if not region_parts:
            continue

        region_name = " > ".join(region_parts)

        for month_col in month_columns:

            match = re.fullmatch(
                r"(\d{4})년\s*(\d{1,2})월",
                str(month_col).strip()
            )

            year = int(match.group(1))
            month = int(match.group(2))

            value = str(row[month_col]).replace(",", "").strip()

            value = pd.to_numeric(
                value,
                errors="coerce"
            )

            if pd.notna(value):

                records.append({
                    "지역": region_name,
                    "연도": year,
                    "월": month,
                    "날짜": pd.Timestamp(
                        year=year,
                        month=month,
                        day=1
                    ),
                    "전환율": float(value)
                })

    result = pd.DataFrame(records)

    if result.empty:
        raise ValueError("분석할 수 있는 전환율 데이터가 없습니다.")

    return result.sort_values(
        ["지역", "날짜"]
    ).reset_index(drop=True)


try:

    data = load_data(str(CSV_FILE))

except Exception as e:

    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.exception(e)
    st.stop()


# ==========================================
# 4. 지역 및 연도 선택
# ==========================================

regions = sorted(data["지역"].unique())

years = sorted(data["연도"].unique())

col1, col2 = st.columns(2)

with col1:

    selected_region = st.selectbox(
        "📍 지역 선택",
        regions
    )

with col2:

    selected_year = st.selectbox(
        "📅 연도 선택",
        years,
        index=len(years) - 1,
        format_func=lambda x: f"{x}년"
    )


# ==========================================
# 5. 선택한 지역과 연도 데이터
# ==========================================

selected = data[
    (data["지역"] == selected_region)
    & (data["연도"] == selected_year)
].copy()

selected = selected.sort_values("날짜")

st.divider()

st.subheader(
    f"📊 {selected_region} / {selected_year}년 전월세 전환율"
)

if selected.empty:

    st.warning("선택한 조건에 데이터가 없습니다.")
    st.stop()


# ==========================================
# 6. 선형회귀 계산 함수
# ==========================================

def calculate_regression(x, y):

    n = len(x)

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    numerator = sum(
        (x[i] - mean_x) * (y[i] - mean_y)
        for i in range(n)
    )

    denominator = sum(
        (x[i] - mean_x) ** 2
        for i in range(n)
    )

    if denominator == 0:
        return None

    slope = numerator / denominator

    intercept = mean_y - slope * mean_x

    return slope, intercept


# ==========================================
# 7. 과거 데이터로 학습
# ==========================================

# 선택한 연도의 마지막 달까지의 과거 자료를 활용합니다.

history = data[
    (data["지역"] == selected_region)
    & (data["날짜"] <= selected["날짜"].max())
].copy()

history = history.sort_values("날짜")

history["월순번"] = (
    history["날짜"].dt.year * 12
    + history["날짜"].dt.month
)

fig = go.Figure()

# 실제 데이터
fig.add_trace(
    go.Scatter(
        x=selected["날짜"],
        y=selected["전환율"],
        mode="lines+markers",
        name="실제 전환율",
        line=dict(width=3),
        marker=dict(size=9)
    )
)

prediction = None
next_date = None

if len(history) >= 2:

    x = history["월순번"].tolist()
    y = history["전환율"].tolist()

    result = calculate_regression(x, y)

    if result is not None:

        slope, intercept = result

        # 다음 달 계산
        last_date = history["날짜"].max()

        next_date = last_date + pd.DateOffset(months=1)

        next_x = next_date.year * 12 + next_date.month

        prediction = slope * next_x + intercept

        # 회귀 직선
        first_x = (
            selected["날짜"].min().year * 12
            + selected["날짜"].min().month
        )

        line_x = list(range(first_x, next_x + 1))

        line_dates = [
            pd.Timestamp(
                year=(v - 1) // 12,
                month=((v - 1) % 12) + 1,
                day=1
            )
            for v in line_x
        ]

        line_y = [
            slope * v + intercept
            for v in line_x
        ]

        fig.add_trace(
            go.Scatter(
                x=line_dates,
                y=line_y,
                mode="lines",
                name="선형회귀 추세선",
                line=dict(
                    dash="dash",
                    width=2
                )
            )
        )

        # 잔차 표시
        fitted = [
            slope * value + intercept
            for value in x
        ]

        residual_x = []
        residual_y = []

        for date, actual, predicted in zip(
            history["날짜"],
            y,
            fitted
        ):

            if date.year == selected_year:

                residual_x.extend([
                    date,
                    date,
                    None
                ])

                residual_y.extend([
                    actual,
                    predicted,
                    None
                ])

        fig.add_trace(
            go.Scatter(
                x=residual_x,
                y=residual_y,
                mode="lines",
                name="실제값과 회귀선의 차이",
                line=dict(
                    dash="dot",
                    width=1
                ),
                hoverinfo="skip"
            )
        )

        # 다음 달 예측값
        fig.add_trace(
            go.Scatter(
                x=[next_date],
                y=[prediction],
                mode="markers",
                name="다음 달 예측값",
                marker=dict(
                    size=17,
                    symbol="star"
                )
            )
        )

else:

    st.warning(
        "예측에 필요한 월별 데이터가 부족합니다. "
        "최소 2개월 이상의 자료가 필요합니다."
    )


# ==========================================
# 8. 그래프 출력
# ==========================================

fig.update_layout(
    template="plotly_white",
    height=520,
    xaxis_title="월",
    yaxis_title="전월세 전환율(%)",
    hovermode="x unified",
    legend_title="그래프 항목"
)

fig.update_yaxes(ticksuffix="%")

fig.update_xaxes(
    tickformat="%Y년 %m월"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 9. 예측 결과 출력
# ==========================================

c1, c2, c3 = st.columns(3)

latest_value = selected.iloc[-1]["전환율"]

c1.metric(
    "선택 연도 데이터",
    f"{len(selected)}개월"
)

c2.metric(
    "최근 실제 전환율",
    f"{latest_value:.2f}%"
)

if prediction is not None:

    c3.metric(
        "다음 달 예측 전환율",
        f"{prediction:.2f}%",
        delta=f"{prediction - latest_value:+.2f}%p"
    )

    st.success(
        f"{next_date.year}년 {next_date.month}월 "
        f"예측 전환율: {prediction:.2f}%"
    )

else:

    c3.metric(
        "예측 전환율",
        "예측 불가"
    )


# ==========================================
# 10. 데이터 표
# ==========================================

with st.expander("📋 월별 실제 데이터 확인"):

    table = selected[
        ["날짜", "전환율"]
    ].copy()

    table["날짜"] = table["날짜"].dt.strftime(
        "%Y년 %m월"
    )

    table.columns = [
        "월",
        "전월세 전환율(%)"
    ]

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 11. 선형회귀 알고리즘 설명
# ==========================================

st.divider()

st.subheader("💡 선형회귀 알고리즘 알아보기")

st.markdown("""
### ① 선형회귀란?

선형회귀(Linear Regression)는 과거 데이터의 관계를
가장 잘 설명하는 직선을 찾아 미래의 값을 예측하는 알고리즘입니다.

### ② 어떻게 작동할까요?

1. 과거 월별 전월세 전환율 데이터를 수집합니다.
2. 각 월의 전환율을 그래프의 점으로 표시합니다.
3. 실제 데이터와 가장 가까운 회귀 직선을 계산합니다.
4. 직선을 다음 달까지 연장하여 전환율을 예측합니다.

### ③ 그래프 읽는 방법

- 실선과 원형 점: 실제 전월세 전환율
- 점선: 선형회귀 알고리즘이 계산한 추세선
- 세로 점선: 실제값과 회귀선의 차이인 잔차
- 별 모양 점: 다음 달 예측 전환율

### ④ 선형회귀의 특징

선형회귀는 데이터의 전체적인 증가 또는 감소 추세를
직선으로 표현한다는 장점이 있습니다.

다만 금리, 정부 정책, 부동산 시장의 급격한 변화 등은
자동으로 반영하지 못합니다.

따라서 예측 결과는 실제 미래의 전환율이 아니라
과거 데이터에 기반한 추정값입니다.
""")

st.caption(
    f"분석 파일: {CSV_FILE.name}"
)

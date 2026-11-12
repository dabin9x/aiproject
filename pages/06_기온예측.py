
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.linear_model import LinearRegression


# --------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------

st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 선형회귀를 이용한 월별 평균기온 예측")
st.markdown(
    "과거 기온 데이터를 학습하여 미래의 평균기온을 예측합니다."
)

st.divider()


# --------------------------------------------------
# 2. CSV 파일 불러오기
# CSV 파일은 app.py 또는 pages 폴더의 상위 폴더에 배치
# --------------------------------------------------

@st.cache_data
def load_data():

    current_dir = Path(__file__).resolve().parent

    possible_paths = [
        current_dir / "temperature.csv",
        current_dir / "temperature (1).csv",
        current_dir.parent / "temperature.csv",
        current_dir.parent / "temperature (1).csv"
    ]

    file_path = None

    for path in possible_paths:
        if path.exists():
            file_path = path
            break

    if file_path is None:
        raise FileNotFoundError(
            "temperature.csv 파일을 찾을 수 없습니다. "
            "app.py와 같은 폴더 또는 상위 폴더에 CSV를 넣어주세요."
        )

    # 한글 CSV 인코딩 자동 대응
    for encoding in ["cp949", "utf-8-sig", "euc-kr", "utf-8"]:
        try:
            data = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("CSV 파일의 인코딩을 읽을 수 없습니다.")

    data.columns = data.columns.str.strip()

    required_columns = ["일시", "평균기온(℃)"]

    for col in required_columns:
        if col not in data.columns:
            raise ValueError(
                f"CSV 파일에 '{col}' 컬럼이 없습니다."
            )

    # 기온을 숫자로 변환
    data["평균기온(℃)"] = pd.to_numeric(
        data["평균기온(℃)"],
        errors="coerce"
    )

    # 영문 월 이름
    month_dict = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    # 일시를 연도와 월로 분리
    def parse_date(value):

        value = str(value).strip()
        parts = value.replace("/", "-").replace(".", "-").split("-")

        try:
            if len(parts) < 2:
                return pd.Series([np.nan, np.nan])

            first = parts[0].strip()
            second = parts[1].strip()

            if first[:3].title() in month_dict:
                month = month_dict[first[:3].title()]
                year = int(second)

            else:
                year = int(first)
                month = int(second)

            # 두 자리 연도 처리
            if year < 100:
                year = 2000 + year if year <= 69 else 1900 + year

            if month < 1 or month > 12:
                return pd.Series([np.nan, np.nan])

            return pd.Series([year, month])

        except (ValueError, TypeError):
            return pd.Series([np.nan, np.nan])

    data[["연도", "월"]] = data["일시"].apply(parse_date)

    data = data.dropna(
        subset=["연도", "월", "평균기온(℃)"]
    )

    data["연도"] = data["연도"].astype(int)
    data["월"] = data["월"].astype(int)

    data = data.sort_values(["연도", "월"])

    return data


# --------------------------------------------------
# 3. 데이터 불러오기
# --------------------------------------------------

try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


if df.empty:
    st.error("분석할 데이터가 없습니다.")
    st.stop()


# --------------------------------------------------
# 4. 데이터 정보
# --------------------------------------------------

st.subheader("📊 기온 데이터 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("전체 데이터 수", f"{len(df):,}개")

with col2:
    st.metric("시작 연도", f"{df['연도'].min()}년")

with col3:
    st.metric("마지막 연도", f"{df['연도'].max()}년")


st.divider()


# --------------------------------------------------
# 5. 사용자 입력
# --------------------------------------------------

st.subheader("🔍 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:

    selected_month = st.selectbox(
        "예측할 월을 선택하세요",
        options=list(range(1, 13)),
        format_func=lambda x: f"{x}월",
        index=0
    )

with col2:

    latest_year = int(df["연도"].max())

    prediction_year = st.number_input(
        "예측할 연도를 입력하세요",
        min_value=int(df["연도"].min()),
        max_value=2100,
        value=latest_year + 1,
        step=1
    )

st.divider()


# --------------------------------------------------
# 6. 선택한 월의 데이터 추출
# --------------------------------------------------

chart_df = df[
    df["월"] == selected_month
].copy()

chart_df = chart_df.sort_values("연도")

if len(chart_df) < 2:
    st.warning(
        f"{selected_month}월의 데이터가 2개 미만이므로 "
        "선형회귀 예측을 할 수 없습니다."
    )
    st.stop()


# --------------------------------------------------
# 7. 선형회귀 모델 생성 및 학습
# --------------------------------------------------

X = chart_df[["연도"]]

y = chart_df["평균기온(℃)"]

model = LinearRegression()

model.fit(X, y)


# --------------------------------------------------
# 8. 예측 기온 계산
# --------------------------------------------------

prediction = model.predict(
    pd.DataFrame({"연도": [int(prediction_year)]})
)[0]

slope = model.coef_[0]

intercept = model.intercept_

r2 = model.score(X, y)


# --------------------------------------------------
# 9. 회귀 직선 데이터 생성
# --------------------------------------------------

line_start = min(
    int(chart_df["연도"].min()),
    int(prediction_year)
)

line_end = max(
    int(chart_df["연도"].max()),
    int(prediction_year)
)

line_years = np.linspace(
    line_start,
    line_end,
    200
)

line_predictions = model.predict(
    pd.DataFrame({"연도": line_years})
)


# --------------------------------------------------
# 10. 그래프 만들기
# --------------------------------------------------

st.subheader(
    f"📈 {selected_month}월 평균기온 및 미래 예측 그래프"
)

fig = go.Figure()


# (1) 실제 관측 기온
fig.add_trace(
    go.Scatter(
        x=chart_df["연도"],
        y=chart_df["평균기온(℃)"],
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            color="royalblue",
            size=11,
            line=dict(width=1, color="white")
        ),
        hovertemplate=
        "%{x}년 실제 평균기온: %{y:.1f}℃<extra></extra>"
    )
)


# (2) 실제값과 회귀선 사이의 오차
residual_x = []
residual_y = []

fitted_values = model.predict(X)

for year, actual, fitted in zip(
    chart_df["연도"],
    y,
    fitted_values
):

    residual_x.extend([year, year, None])

    residual_y.extend([actual, fitted, None])


fig.add_trace(
    go.Scatter(
        x=residual_x,
        y=residual_y,
        mode="lines",
        name="예측 오차(잔차)",
        line=dict(
            color="gray",
            width=1,
            dash="dot"
        ),
        hoverinfo="skip"
    )
)


# (3) 선형회귀 직선
fig.add_trace(
    go.Scatter(
        x=line_years,
        y=line_predictions,
        mode="lines",
        name="선형회귀 예측 직선",
        line=dict(
            color="red",
            width=3
        ),
        hovertemplate=
        "연도: %{x:.1f}<br>회귀 예측: %{y:.2f}℃<extra></extra>"
    )
)


# (4) 미래 예측 기온
fig.add_trace(
    go.Scatter(
        x=[prediction_year],
        y=[prediction],
        mode="markers+text",
        name="미래 예측 기온",
        marker=dict(
            color="green",
            size=17,
            symbol="star"
        ),
        text=[f"{prediction:.1f}℃"],
        textposition="top center",
        textfont=dict(size=15),
        hovertemplate=
        f"{prediction_year}년 예측 기온: %{{y:.2f}}℃<extra></extra>"
    )
)


# (5) 예측 연도 표시
fig.add_vline(
    x=prediction_year,
    line_width=1,
    line_dash="dash",
    line_color="green"
)


fig.update_layout(
    title=dict(
        text=f"{selected_month}월 평균기온 선형회귀 분석",
        x=0.5
    ),

    xaxis_title="연도",

    yaxis_title="평균기온 (℃)",

    hovermode="closest",

    template="plotly_white",

    height=600,

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),

    font=dict(
        size=13
    )
)

fig.update_xaxes(
    dtick=1,
    showgrid=True
)

fig.update_yaxes(
    showgrid=True,
    zeroline=True
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------------------------
# 11. 예측 결과
# --------------------------------------------------

st.subheader("🎯 기온 예측 결과")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        label=f"{prediction_year}년 {selected_month}월 예측 평균기온",
        value=f"{prediction:.2f}℃"
    )

with col2:

    st.metric(
        label="회귀 직선의 기울기",
        value=f"{slope:.4f}℃/년"
    )

with col3:

    st.metric(
        label="결정계수 (R²)",
        value=f"{r2:.4f}"
    )


# --------------------------------------------------
# 12. 선형회귀 알고리즘 설명
# --------------------------------------------------

st.divider()

st.subheader("📚 선형회귀(Linear Regression) 알고리즘 이해하기")

st.markdown("""
### ① 선형회귀란?

선형회귀는 과거의 데이터를 분석하여 데이터 사이에 존재하는
직선 형태의 관계를 찾아내고, 이를 이용하여 미래의 값을 예측하는
머신러닝 알고리즘입니다.

이번 프로그램에서는 다음과 같이 적용합니다.

- 독립변수 X : 연도
- 종속변수 Y : 해당 월의 평균기온
- 학습 데이터 : temperature.csv에 기록된 과거 평균기온
- 예측 데이터 : 사용자가 입력한 미래 연도

### ② 선형회귀의 기본 원리

선형회귀는 다음 수식으로 표현됩니다.

""")

st.latex(r"\hat{y} = b_0 + b_1 x")

st.markdown("""
- x : 연도
- ŷ : 예측 평균기온
- b₀ : 절편
- b₁ : 기울기

기울기는 연도가 1년 증가할 때 평균기온이 얼마나 변하는지를
나타냅니다.

### ③ 그래프는 알고리즘의 작동을 어떻게 보여줄까?

그래프의 각 요소는 다음과 같은 의미를 가집니다.

| 그래프 요소 | 의미 |
|---|---|
| 파란색 점 | 실제 관측된 평균기온 |
| 빨간색 직선 | 선형회귀가 학습한 최적의 직선 |
| 회색 점선 | 실제 기온과 회귀선 사이의 오차 |
| 초록색 별 | 입력한 연도의 예측 기온 |

선형회귀 알고리즘은 실제 데이터와 직선 사이의 오차 제곱합이
최소가 되도록 직선을 결정합니다.

이 방법을 최소제곱법(Ordinary Least Squares)이라고 합니다.

### ④ 결정계수(R²)란?

결정계수는 회귀모델이 과거 데이터의 변동을 얼마나 설명하는지
보여주는 지표입니다.

- 1에 가까울수록 과거 데이터에 대한 설명력이 높습니다.
- 0에 가까우면 과거 데이터의 변동을 설명하는 정도가 낮습니다.
- 음수가 나올 수도 있습니다.

결정계수가 높다고 미래 예측이 반드시 정확한 것은 아닙니다.
특히 먼 미래를 예측할 때는 주의해야 합니다.

""")

# 현재 분석 결과를 이용한 설명
st.info(
    f"""
    **현재 {selected_month}월 분석 결과**

    - 학습에 사용한 데이터: {len(chart_df)}개
    - 회귀 직선의 기울기: {slope:.4f}℃/년
    - 결정계수: {r2:.4f}
    - {prediction_year}년 예측 평균기온: {prediction:.2f}℃

    기울기가 양수이면 과거 데이터에서 기온이 상승하는 경향을,
    음수이면 하락하는 경향을 나타냅니다.
    """
)


# --------------------------------------------------
# 13. 실제 데이터 확인
# --------------------------------------------------

with st.expander("📋 선택한 월의 실제 기온 데이터 확인하기"):

    display_df = chart_df[
        ["연도", "월", "평균기온(℃)"]
    ].copy()

    display_df.columns = [
        "연도",
        "월",
        "실제 평균기온(℃)"
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


st.caption(
    "※ 본 프로그램은 과거 기온과 연도 사이의 선형 관계를 이용한 "
    "단순 예측 모델입니다. 실제 기온은 기후변화, 강수량, "
    "대기 흐름 등 다양한 요인에 따라 달라질 수 있습니다."
)

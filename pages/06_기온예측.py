
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor


# ==================================================
# 1. 페이지 설정
# ==================================================

st.set_page_config(
    page_title="AI 월별 기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ AI 월별 평균기온 예측 프로그램")

st.markdown("""
과거의 기온 데이터를 학습하여 미래의 기온을 예측합니다.

**3가지 회귀 알고리즘의 예측 결과를 직접 비교해 보세요!**
""")

st.divider()


# ==================================================
# 2. CSV 파일 불러오기
# ==================================================

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
            "temperature.csv 파일을 찾을 수 없습니다."
        )

    data = None

    for encoding in ["cp949", "utf-8-sig", "euc-kr", "utf-8"]:

        try:
            data = pd.read_csv(
                file_path,
                encoding=encoding
            )
            break

        except UnicodeDecodeError:
            continue

    if data is None:
        raise ValueError("CSV 인코딩을 확인해 주세요.")

    data.columns = data.columns.str.strip()

    if "일시" not in data.columns:
        raise ValueError("'일시' 컬럼이 없습니다.")

    if "평균기온(℃)" not in data.columns:
        raise ValueError("'평균기온(℃)' 컬럼이 없습니다.")

    data["평균기온(℃)"] = pd.to_numeric(
        data["평균기온(℃)"],
        errors="coerce"
    )

    month_dict = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

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

            if year < 100:
                year = 2000 + year if year <= 69 else 1900 + year

            if month < 1 or month > 12:
                return pd.Series([np.nan, np.nan])

            return pd.Series([year, month])

        except (ValueError, TypeError):

            return pd.Series([np.nan, np.nan])

    data[["연도", "월"]] = data["일시"].apply(
        parse_date
    )

    data = data.dropna(
        subset=["연도", "월", "평균기온(℃)"]
    )

    data["연도"] = data["연도"].astype(int)
    data["월"] = data["월"].astype(int)

    data = data.sort_values(
        ["연도", "월"]
    )

    return data


try:

    df = load_data()

except Exception as e:

    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


if df.empty:

    st.error("분석할 데이터가 없습니다.")
    st.stop()


# ==================================================
# 3. 데이터 정보
# ==================================================

st.subheader("📊 기온 데이터 정보")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "전체 데이터",
        f"{len(df):,}개"
    )

with c2:
    st.metric(
        "시작 연도",
        f"{df['연도'].min()}년"
    )

with c3:
    st.metric(
        "마지막 연도",
        f"{df['연도'].max()}년"
    )

st.divider()


# ==================================================
# 4. 사용자 입력
# ==================================================

st.subheader("🔍 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:

    selected_month = st.selectbox(
        "예측할 월",
        list(range(1, 13)),
        format_func=lambda x: f"{x}월"
    )


chart_df = df[
    df["월"] == selected_month
].copy()

chart_df = chart_df.sort_values("연도")


if len(chart_df) < 3:

    st.warning(
        "선택한 월의 데이터가 부족합니다. "
        "최소 3개 이상의 데이터가 필요합니다."
    )

    st.stop()


latest_month_year = int(chart_df["연도"].max())

with col2:

    prediction_year = st.number_input(
        "예측할 연도",
        min_value=latest_month_year + 1,
        max_value=2100,
        value=latest_month_year + 1,
        step=1
    )


# ==================================================
# 5. 회귀 알고리즘 선택
# ==================================================

st.divider()

st.subheader("🤖 회귀 알고리즘 선택")

algorithm_names = [
    "선형회귀 (Linear Regression)",
    "다항회귀 (Polynomial Regression)",
    "랜덤 포레스트 회귀 (Random Forest)"
]

selected_algorithm = st.selectbox(
    "사용할 예측 알고리즘을 선택하세요.",
    algorithm_names
)


# ==================================================
# 6. 학습 데이터 준비
# ==================================================

X = chart_df[["연도"]]

y = chart_df["평균기온(℃)"]


# ==================================================
# 7. 3가지 회귀 알고리즘 생성
# ==================================================

models = {

    "선형회귀 (Linear Regression)": LinearRegression(),

    "다항회귀 (Polynomial Regression)": make_pipeline(
        PolynomialFeatures(
            degree=2,
            include_bias=False
        ),
        LinearRegression()
    ),

    "랜덤 포레스트 회귀 (Random Forest)": RandomForestRegressor(
        n_estimators=300,
        max_depth=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

}


# ==================================================
# 8. 3가지 알고리즘 모두 학습
# ==================================================

prediction_results = {}
r2_results = {}
trained_models = {}

for name, model in models.items():

    model.fit(X, y)

    trained_models[name] = model

    future_X = pd.DataFrame({
        "연도": [int(prediction_year)]
    })

    future_prediction = model.predict(
        future_X
    )[0]

    prediction_results[name] = future_prediction

    r2_results[name] = model.score(X, y)


# ==================================================
# 9. 선택한 알고리즘 결과
# ==================================================

selected_model = trained_models[selected_algorithm]

selected_prediction = prediction_results[selected_algorithm]

selected_r2 = r2_results[selected_algorithm]


# ==================================================
# 10. 회귀선 생성
# ==================================================

line_start = int(chart_df["연도"].min())

line_end = int(prediction_year)

line_years = np.linspace(
    line_start,
    line_end,
    500
)

line_X = pd.DataFrame({
    "연도": line_years
})

line_predictions = selected_model.predict(
    line_X
)


# ==================================================
# 11. 그래프
# ==================================================

st.divider()

st.subheader(
    f"📈 {selected_month}월 평균기온 예측 그래프"
)

st.markdown(
    f"현재 선택된 알고리즘: **{selected_algorithm}**"
)

fig = go.Figure()


# 실제 기온
fig.add_trace(
    go.Scatter(
        x=chart_df["연도"],
        y=chart_df["평균기온(℃)"],
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            color="royalblue",
            size=10
        ),
        hovertemplate=
        "%{x}년 실제 기온: %{y:.2f}℃<extra></extra>"
    )
)


# 선택된 모델의 학습 예측값
fitted_values = selected_model.predict(X)

residual_x = []
residual_y = []

for year, actual, fitted in zip(
    chart_df["연도"],
    y,
    fitted_values
):

    residual_x.extend([year, year, None])
    residual_y.extend([actual, fitted, None])


# 실제값과 예측값의 오차
fig.add_trace(
    go.Scatter(
        x=residual_x,
        y=residual_y,
        mode="lines",
        name="예측 오차",
        line=dict(
            color="gray",
            width=1,
            dash="dot"
        ),
        hoverinfo="skip"
    )
)


# 선택된 알고리즘의 회귀선
fig.add_trace(
    go.Scatter(
        x=line_years,
        y=line_predictions,
        mode="lines",
        name="선택한 알고리즘의 회귀선",
        line=dict(
            color="red",
            width=3
        ),
        hovertemplate=
        "연도: %{x:.1f}<br>예측 기온: %{y:.2f}℃<extra></extra>"
    )
)


# 미래 예측값
fig.add_trace(
    go.Scatter(
        x=[prediction_year],
        y=[selected_prediction],
        mode="markers+text",
        name="미래 예측 기온",
        marker=dict(
            color="green",
            size=18,
            symbol="star"
        ),
        text=[f"{selected_prediction:.2f}℃"],
        textposition="top center",
        textfont=dict(size=15),
        hovertemplate=
        f"{prediction_year}년 예측 기온: %{{y:.2f}}℃<extra></extra>"
    )
)


# 미래 연도 표시
fig.add_vline(
    x=prediction_year,
    line_dash="dash",
    line_color="green",
    line_width=1
)


fig.update_layout(

    title=dict(
        text=f"{selected_month}월 평균기온 - {selected_algorithm}",
        x=0.5
    ),

    xaxis_title="연도",

    yaxis_title="평균기온 (℃)",

    height=600,

    template="plotly_white",

    hovermode="closest",

    legend=dict(
        orientation="h",
        y=1.12,
        x=0.5,
        xanchor="center"
    ),

    font=dict(size=13)

)

fig.update_xaxes(
    showgrid=True,
    dtick=2
)

fig.update_yaxes(
    showgrid=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==================================================
# 12. 선택된 알고리즘 예측 결과
# ==================================================

st.subheader("🎯 선택한 알고리즘의 예측 결과")

c1, c2 = st.columns(2)

with c1:

    st.metric(
        f"{prediction_year}년 {selected_month}월 예측 기온",
        f"{selected_prediction:.2f}℃"
    )

with c2:

    st.metric(
        "학습 데이터 결정계수 R²",
        f"{selected_r2:.4f}"
    )


# ==================================================
# 13. 3가지 알고리즘 예측값 비교
# ==================================================

st.divider()

st.subheader("🏆 3가지 회귀 알고리즘 예측 결과 비교")

st.markdown("""
같은 과거 데이터와 같은 예측 연도를 사용하더라도
알고리즘에 따라 예측 결과가 어떻게 달라지는지 확인해 보세요.
""")

comparison_df = pd.DataFrame({

    "알고리즘": list(prediction_results.keys()),

    "예측 평균기온(℃)": [
        round(v, 2)
        for v in prediction_results.values()
    ],

    "학습 데이터 R²": [
        round(v, 4)
        for v in r2_results.values()
    ]

})

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)


# 예측 기온 비교 그래프
comparison_fig = go.Figure()

comparison_fig.add_trace(
    go.Bar(
        x=list(prediction_results.keys()),
        y=list(prediction_results.values()),
        text=[
            f"{v:.2f}℃"
            for v in prediction_results.values()
        ],
        textposition="outside",
        marker_color=[
            "royalblue",
            "orange",
            "seagreen"
        ]
    )
)

comparison_fig.update_layout(
    title=f"{prediction_year}년 {selected_month}월 알고리즘별 예측 기온",
    xaxis_title="회귀 알고리즘",
    yaxis_title="예측 평균기온 (℃)",
    template="plotly_white",
    height=430,
    showlegend=False
)

st.plotly_chart(
    comparison_fig,
    use_container_width=True
)


# ==================================================
# 14. 알고리즘 설명
# ==================================================

st.divider()

st.subheader("📚 회귀 알고리즘의 작동 원리")

st.markdown("""
### ① 선형회귀 (Linear Regression)

선형회귀는 과거 데이터에 가장 잘 맞는 직선을 찾는 알고리즘입니다.

기본 수식은 다음과 같습니다.

""")

st.latex(r"\hat{y}=b_0+b_1x")

st.markdown("""
- X : 연도
- Y : 평균기온
- b₀ : 절편
- b₁ : 기울기

실제 데이터와 직선 사이의 오차 제곱합이 최소가 되도록
직선을 결정합니다.

**특징:** 일정한 상승 또는 하락 추세를 예측하는 데 적합합니다.

---

### ② 다항회귀 (Polynomial Regression)

다항회귀는 직선 대신 곡선 형태의 관계를 학습하는 알고리즘입니다.

이번 프로그램은 2차 다항회귀를 사용합니다.

""")

st.latex(
    r"\hat{y}=b_0+b_1x+b_2x^2"
)

st.markdown("""
- X : 연도
- X² : 연도의 제곱
- b₀, b₁, b₂ : 학습을 통해 구하는 계수

과거 데이터에 곡선 형태의 패턴이 있다면
선형회귀보다 유연하게 표현할 수 있습니다.

**특징:** 직선으로 설명하기 어려운 곡선 형태의 추세를 학습합니다.

---

### ③ 랜덤 포레스트 회귀 (Random Forest Regression)

랜덤 포레스트는 여러 개의 의사결정나무를 만들어
각 나무의 예측값을 평균하여 최종 결과를 계산합니다.

""")

st.latex(
    r"\hat{y}=\frac{1}{N}\sum_{i=1}^{N}\hat{y}_i"
)

st.markdown("""
- N : 의사결정나무의 개수
- ŷᵢ : 각각의 의사결정나무가 예측한 값
- ŷ : 최종 예측값

이번 프로그램에서는 300개의 의사결정나무를 사용합니다.

**특징:** 복잡하고 비선형적인 데이터 패턴을 학습할 수 있습니다.

다만 과거 학습 범위 밖의 미래 연도를 입력하면
랜덤 포레스트는 일반적으로 학습 데이터 범위를 벗어난
새로운 기온 추세를 만들어내지 못합니다.
따라서 미래 장기 예측에서는 주의해야 합니다.

---

### ④ 알고리즘별 차이점

| 알고리즘 | 학습하는 형태 | 주요 특징 |
|---|---|---|
| 선형회귀 | 직선 | 일정한 추세 |
| 다항회귀 | 곡선 | 곡선 형태의 추세 |
| 랜덤 포레스트 | 여러 나무의 평균 | 복잡한 패턴 |

""")

# ==================================================
# 15. 선택된 알고리즘에 대한 해석
# ==================================================

st.subheader("💡 현재 선택한 알고리즘 분석")

if selected_algorithm == algorithm_names[0]:

    st.info("""
    **선형회귀를 선택했습니다.**

    과거의 평균기온이 연도에 따라 얼마나 상승하거나
    하락하는지를 직선으로 학습합니다.

    회귀선의 기울기를 통해 연평균 변화 방향을 파악할 수 있습니다.
    """)

    st.latex(
        rf"\hat{{y}}={selected_model.intercept_:.4f}"
        rf"+({selected_model.coef_[0]:.4f})x"
    )

elif selected_algorithm == algorithm_names[1]:

    poly_model = selected_model

    coefficients = poly_model.named_steps[
        "linearregression"
    ].coef_

    intercept = poly_model.named_steps[
        "linearregression"
    ].intercept_

    st.info("""
    **2차 다항회귀를 선택했습니다.**

    직선이 아니라 곡선을 이용해 과거 기온의 패턴을 학습합니다.
    기온 변화가 일정하지 않은 데이터에서 선형회귀와
    다른 결과를 보여줄 수 있습니다.
    """)

    st.latex(
        rf"\hat{{y}}={intercept:.4f}"
        rf"+({coefficients[0]:.4f})x"
        rf"+({coefficients[1]:.8f})x^2"
    )

else:

    st.info("""
    **랜덤 포레스트 회귀를 선택했습니다.**

    여러 의사결정나무의 예측 결과를 평균하여
    최종 기온을 계산합니다.

    복잡한 패턴을 학습할 수 있지만,
    과거 데이터 범위를 벗어난 미래 예측에는 한계가 있습니다.
    """)


# ==================================================
# 16. 실제 데이터 확인
# ==================================================

with st.expander("📋 실제 기온 데이터 확인하기"):

    show_df = chart_df[
        ["연도", "월", "평균기온(℃)"]
    ].copy()

    show_df.columns = [
        "연도",
        "월",
        "평균기온(℃)"
    ]

    st.dataframe(
        show_df,
        use_container_width=True,
        hide_index=True
    )


st.divider()

st.caption("""
※ 본 프로그램은 과거 월별 평균기온과 연도의 관계를 학습하는
교육용 예측 프로그램입니다.

※ 학습 데이터의 R²는 과거 데이터에 대한 설명력이며
미래 예측의 정확도를 보장하지 않습니다.

※ 기온은 다양한 기후 요인의 영향을 받으므로
실제 미래 기온과 예측값은 다를 수 있습니다.
""")

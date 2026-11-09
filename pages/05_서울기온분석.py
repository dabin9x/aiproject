
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="서울 월별 기온 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 월별 기온 분석")
st.markdown(
    "서울의 월별 평균기온과 연도별 최고·최저기온을 비교해 보세요."
)

st.divider()

# ==========================================
# 2. 상위 폴더 CSV 파일 불러오기
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

file_path = BASE_DIR / "extremum_20261109105046 (1).csv"

try:
    df = pd.read_csv(
        file_path,
        encoding="cp949",
        skiprows=11,
        skipinitialspace=True
    )

except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.write("파일 경로:", str(file_path))
    st.stop()

except Exception as e:
    st.error(f"데이터 파일을 읽을 수 없습니다: {e}")
    st.stop()

# ==========================================
# 3. 데이터 전처리
# ==========================================

df.columns = df.columns.astype(str).str.strip()

required_columns = [
    "일시",
    "평균기온(℃)",
    "최고기온(℃)",
    "최저기온(℃)"
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:
    st.error(f"필요한 컬럼이 없습니다: {missing}")
    st.stop()

# 날짜 변환
df["일시"] = pd.to_datetime(
    df["일시"],
    format="%Y-%m",
    errors="coerce"
)

# 숫자 변환
temperature_columns = [
    "평균기온(℃)",
    "최고기온(℃)",
    "최저기온(℃)"
]

for col in temperature_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# 연도와 월 추출
df["연도"] = df["일시"].dt.year
df["월"] = df["일시"].dt.month

df = df.dropna(
    subset=["연도", "월"]
).copy()

df["연도"] = df["연도"].astype(int)
df["월"] = df["월"].astype(int)

# ==========================================
# 4. 서울 월별 평균기온 분석
# ==========================================

st.header("① 서울 월별 평균기온")

st.write(
    "전체 관측 기간의 자료를 이용하여 "
    "1월부터 12월까지 월별 평균기온을 비교합니다."
)

monthly_avg = (
    df.dropna(subset=["평균기온(℃)"])
    .groupby("월")["평균기온(℃)"]
    .mean()
    .reindex(range(1, 13))
)

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=monthly_avg.index,
        y=monthly_avg.values,
        mode="lines+markers",
        name="월별 평균기온",
        line=dict(
            color="#FF9F43",
            width=3
        ),
        marker=dict(
            size=9,
            color="#FF9F43"
        ),
        hovertemplate=(
            "%{x}월<br>"
            "평균기온: %{y:.1f}℃"
            "<extra></extra>"
        )
    )
)

fig1.update_layout(
    title=dict(
        text="서울 월별 평균기온",
        x=0.5,
        xanchor="center"
    ),
    xaxis=dict(
        title="월",
        tickmode="array",
        tickvals=list(range(1, 13)),
        ticktext=[f"{i}월" for i in range(1, 13)]
    ),
    yaxis=dict(
        title="평균기온(℃)",
        zeroline=True
    ),
    hovermode="x unified",
    template="plotly_white",
    height=450,
    showlegend=True
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# 월별 평균기온 표
with st.expander("월별 평균기온 상세 데이터"):
    avg_table = monthly_avg.reset_index()
    avg_table.columns = ["월", "평균기온(℃)"]
    avg_table["월"] = avg_table["월"].apply(
        lambda x: f"{x}월"
    )
    st.dataframe(
        avg_table,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ==========================================
# 5. 연도 선택 방식
# ==========================================

st.header("② 연도별 최고기온 및 최저기온 분석")

st.write(
    "연도를 1개 또는 2개 선택하여 "
    "월별 최고기온과 최저기온을 비교할 수 있습니다."
)

years = sorted(
    df["연도"].dropna().unique().tolist()
)

if not years:
    st.warning("분석할 연도 데이터가 없습니다.")
    st.stop()

selection_mode = st.radio(
    "분석할 연도 개수 선택",
    options=["연도 1개 선택", "연도 2개 선택"],
    horizontal=True
)

# ==========================================
# 6. 연도 1개 선택
# ==========================================

if selection_mode == "연도 1개 선택":

    selected_year = st.selectbox(
        "분석할 연도를 선택하세요.",
        options=years,
        index=len(years) - 1,
        format_func=lambda x: f"{x}년"
    )

    year_df = df[
        df["연도"] == selected_year
    ].copy()

    # 월별 최고기온과 최저기온
    year_monthly = (
        year_df.groupby("월")
        .agg({
            "최고기온(℃)": "max",
            "최저기온(℃)": "min"
        })
        .reindex(range(1, 13))
    )

    st.subheader(
        f"📊 {selected_year}년 월별 최고·최저기온"
    )

    fig2 = go.Figure()

    # 최고기온 - 연두색
    fig2.add_trace(
        go.Scatter(
            x=year_monthly.index,
            y=year_monthly["최고기온(℃)"],
            mode="lines+markers",
            name="최고기온",
            connectgaps=False,
            line=dict(
                color="#90EE90",
                width=3
            ),
            marker=dict(
                color="#90EE90",
                size=9
            ),
            hovertemplate=(
                "%{x}월<br>"
                "최고기온: %{y:.1f}℃"
                "<extra></extra>"
            )
        )
    )

    # 최저기온 - 하늘색
    fig2.add_trace(
        go.Scatter(
            x=year_monthly.index,
            y=year_monthly["최저기온(℃)"],
            mode="lines+markers",
            name="최저기온",
            connectgaps=False,
            line=dict(
                color="#87CEEB",
                width=3
            ),
            marker=dict(
                color="#87CEEB",
                size=9
            ),
            hovertemplate=(
                "%{x}월<br>"
                "최저기온: %{y:.1f}℃"
                "<extra></extra>"
            )
        )
    )

    fig2.update_layout(
        title=dict(
            text=f"{selected_year}년 월별 기온 분석",
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(
            title="월",
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=[f"{i}월" for i in range(1, 13)]
        ),
        yaxis=dict(
            title="온도(℃)",
            zeroline=True
        ),
        legend=dict(
            title="기온 구분",
            orientation="h",
            y=1.12,
            x=0.5,
            xanchor="center"
        ),
        hovermode="x unified",
        template="plotly_white",
        height=550
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.info(
        "연두색은 최고기온, 하늘색은 최저기온입니다."
    )

    # 상세 데이터
    with st.expander("연도별 상세 데이터 확인"):
        detail = year_monthly.reset_index()
        detail.columns = [
            "월",
            "최고기온(℃)",
            "최저기온(℃)"
        ]
        st.dataframe(
            detail,
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# 7. 연도 2개 선택
# ==========================================

else:

    col1, col2 = st.columns(2)

    with col1:
        year1 = st.selectbox(
            "첫 번째 연도",
            options=years,
            index=len(years) - 2 if len(years) >= 2 else 0,
            format_func=lambda x: f"{x}년",
            key="year1"
        )

    with col2:
        year2 = st.selectbox(
            "두 번째 연도",
            options=years,
            index=len(years) - 1,
            format_func=lambda x: f"{x}년",
            key="year2"
        )

    if year1 == year2:
        st.warning("서로 다른 연도를 선택해 주세요.")

    else:

        data1 = df[df["연도"] == year1]
        data2 = df[df["연도"] == year2]

        monthly1 = (
            data1.groupby("월")
            .agg({
                "최고기온(℃)": "max",
                "최저기온(℃)": "min"
            })
            .reindex(range(1, 13))
        )

        monthly2 = (
            data2.groupby("월")
            .agg({
                "최고기온(℃)": "max",
                "최저기온(℃)": "min"
            })
            .reindex(range(1, 13))
        )

        st.subheader(
            f"📊 {year1}년 vs {year2}년 기온 비교"
        )

        fig3 = go.Figure()

        # 첫 번째 연도 최고기온
        fig3.add_trace(
            go.Scatter(
                x=monthly1.index,
                y=monthly1["최고기온(℃)"],
                mode="lines+markers",
                name=f"{year1}년 최고기온",
                connectgaps=False,
                line=dict(
                    color="#90EE90",
                    width=3
                ),
                marker=dict(size=8),
                hovertemplate=(
                    "%{x}월<br>"
                    f"{year1}년 최고기온: "
                    "%{y:.1f}℃<extra></extra>"
                )
            )
        )

        # 첫 번째 연도 최저기온
        fig3.add_trace(
            go.Scatter(
                x=monthly1.index,
                y=monthly1["최저기온(℃)"],
                mode="lines+markers",
                name=f"{year1}년 최저기온",
                connectgaps=False,
                line=dict(
                    color="#87CEEB",
                    width=3
                ),
                marker=dict(size=8),
                hovertemplate=(
                    "%{x}월<br>"
                    f"{year1}년 최저기온: "
                    "%{y:.1f}℃<extra></extra>"
                )
            )
        )

        # 두 번째 연도 최고기온
        fig3.add_trace(
            go.Scatter(
                x=monthly2.index,
                y=monthly2["최고기온(℃)"],
                mode="lines+markers",
                name=f"{year2}년 최고기온",
                connectgaps=False,
                line=dict(
                    color="#90EE90",
                    width=3,
                    dash="dash"
                ),
                marker=dict(
                    size=8,
                    symbol="diamond"
                ),
                hovertemplate=(
                    "%{x}월<br>"
                    f"{year2}년 최고기온: "
                    "%{y:.1f}℃<extra></extra>"
                )
            )
        )

        # 두 번째 연도 최저기온
        fig3.add_trace(
            go.Scatter(
                x=monthly2.index,
                y=monthly2["최저기온(℃)"],
                mode="lines+markers",
                name=f"{year2}년 최저기온",
                connectgaps=False,
                line=dict(
                    color="#87CEEB",
                    width=3,
                    dash="dash"
                ),
                marker=dict(
                    size=8,
                    symbol="diamond"
                ),
                hovertemplate=(
                    "%{x}월<br>"
                    f"{year2}년 최저기온: "
                    "%{y:.1f}℃<extra></extra>"
                )
            )
        )

        fig3.update_layout(
            title=dict(
                text=f"{year1}년과 {year2}년 월별 기온 비교",
                x=0.5,
                xanchor="center"
            ),
            xaxis=dict(
                title="월",
                tickmode="array",
                tickvals=list(range(1, 13)),
                ticktext=[
                    f"{i}월" for i in range(1, 13)
                ]
            ),
            yaxis=dict(
                title="온도(℃)",
                zeroline=True
            ),
            legend=dict(
                title="연도 및 기온 구분",
                orientation="h",
                y=1.15,
                x=0.5,
                xanchor="center"
            ),
            hovermode="x unified",
            template="plotly_white",
            height=600
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

        st.info(
            "실선은 첫 번째 연도, 점선은 두 번째 연도입니다. "
            "연두색은 최고기온, 하늘색은 최저기온입니다."
        )

        # 두 연도 상세 데이터 비교
        with st.expander("두 연도 상세 데이터 확인"):

            comparison = pd.DataFrame({
                "월": range(1, 13),
                f"{year1}년 최고기온": monthly1[
                    "최고기온(℃)"
                ].values,
                f"{year1}년 최저기온": monthly1[
                    "최저기온(℃)"
                ].values,
                f"{year2}년 최고기온": monthly2[
                    "최고기온(℃)"
                ].values,
                f"{year2}년 최저기온": monthly2[
                    "최저기온(℃)"
                ].values
            })

            st.dataframe(
                comparison,
                use_container_width=True,
                hide_index=True
            )

# ==========================================
# 8. 하단 안내
# ==========================================

st.divider()

st.caption(
    "자료: 기상청 기상자료개방포털 | 지역: 서울"
)

st.caption(
    "※ 월별 최고기온은 해당 월에 관측된 최고기온, "
    "월별 최저기온은 해당 월에 관측된 최저기온입니다."
)

st.caption(
    "※ 관측 자료가 없는 월은 그래프에 연결하지 않습니다."
)

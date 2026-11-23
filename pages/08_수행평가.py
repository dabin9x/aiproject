
from pathlib import Path
import re

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# =====================================================
# 1. 페이지 설정
# =====================================================

st.set_page_config(
    page_title="아파트 전월세 전환율 분석",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 전국 아파트 전월세 전환율 종합 대시보드")
st.caption("전국 및 지역별 아파트 전월세 전환율을 한눈에 분석합니다.")


# =====================================================
# 2. CSV 파일 찾기
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CSV_FILE = BASE_DIR / "지역별 전월세 전환율_아파트.csv"

if not CSV_FILE.exists():
    st.error(
        "CSV 파일을 찾을 수 없습니다.\n\n"
        "프로젝트 최상위 폴더에 "
        "'지역별 전월세 전환율_아파트.csv' 파일을 넣어주세요."
    )
    st.stop()


# =====================================================
# 3. CSV 데이터 불러오기 및 정리
# =====================================================

@st.cache_data
def load_data(file_path):

    raw = None

    for encoding in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
        try:
            raw = pd.read_csv(
                file_path,
                encoding=encoding,
                dtype=str
            )
            break
        except UnicodeDecodeError:
            continue

    if raw is None:
        raise ValueError("CSV 파일의 인코딩을 읽을 수 없습니다.")

    raw.columns = [str(c).strip() for c in raw.columns]

    region_columns = ["지역", "지역.1", "지역.2"]

    for col in region_columns:
        if col not in raw.columns:
            raise ValueError(f"CSV에 '{col}' 열이 없습니다.")

    # 월별 데이터 열 찾기
    month_columns = []

    for col in raw.columns:

        match = re.fullmatch(
            r"(\d{4})년\s*(\d{1,2})월",
            str(col).strip()
        )

        if match:
            month_columns.append(col)

    if not month_columns:
        raise ValueError("월별 데이터 열을 찾지 못했습니다.")

    records = []

    # 첫 번째 행은 열 설명이므로 제외
    for _, row in raw.iloc[1:].iterrows():

        parts = []

        for col in region_columns:

            value = row[col]

            if pd.isna(value):
                continue

            value = str(value).strip()

            if value in ("", "-", "nan", "None"):
                continue

            # 연속해서 반복되는 지역명 제거
            if not parts or parts[-1] != value:
                parts.append(value)

        if not parts:
            continue

        region_path = " > ".join(parts)
        region_name = parts[-1]
        region_level = len(parts)

        for month_col in month_columns:

            match = re.fullmatch(
                r"(\d{4})년\s*(\d{1,2})월",
                str(month_col).strip()
            )

            year = int(match.group(1))
            month = int(match.group(2))

            value = pd.to_numeric(
                str(row[month_col]).replace(",", "").strip(),
                errors="coerce"
            )

            if pd.notna(value):

                records.append({
                    "지역경로": region_path,
                    "지역명": region_name,
                    "지역단계": region_level,
                    "연도": year,
                    "월": month,
                    "날짜": pd.Timestamp(year, month, 1),
                    "전환율": float(value)
                })

    df = pd.DataFrame(records)

    if df.empty:
        raise ValueError("분석할 수 있는 전환율 데이터가 없습니다.")

    df = df.sort_values(
        ["지역경로", "날짜"]
    ).reset_index(drop=True)

    return df


try:
    data = load_data(str(CSV_FILE))

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
    st.stop()


# =====================================================
# 4. 사이드바 분석 조건
# =====================================================

st.sidebar.title("⚙️ 분석 설정")

years = sorted(data["연도"].unique())

selected_year = st.sidebar.selectbox(
    "📅 분석 연도",
    years,
    index=len(years) - 1
)

months = sorted(
    data.loc[
        data["연도"] == selected_year,
        "월"
    ].unique()
)

month_options = ["연평균"] + [
    f"{m}월" for m in months
]

selected_month = st.sidebar.selectbox(
    "🗓️ 분석 월",
    month_options
)

available_levels = sorted(
    data["지역단계"].unique()
)

level_names = {
    1: "1단계 지역",
    2: "2단계 지역",
    3: "3단계 지역"
}

selected_level = st.sidebar.selectbox(
    "📍 지역 분석 단계",
    available_levels,
    format_func=lambda x: level_names.get(
        x, f"{x}단계 지역"
    ),
    index=len(available_levels) - 1
)


# =====================================================
# 5. 연도 및 월별 분석 데이터
# =====================================================

year_data = data[
    data["연도"] == selected_year
].copy()

if selected_month == "연평균":

    analysis_data = (
        year_data.groupby(
            ["지역경로", "지역명", "지역단계"],
            as_index=False
        )["전환율"]
        .mean()
    )

    analysis_label = f"{selected_year}년 연평균"

else:

    month_number = int(
        selected_month.replace("월", "")
    )

    analysis_data = year_data[
        year_data["월"] == month_number
    ].copy()

    analysis_label = (
        f"{selected_year}년 {month_number}월"
    )


# 선택한 지역 단계만 추출
level_data = analysis_data[
    analysis_data["지역단계"] == selected_level
].copy()

# 전국 및 일부 요약 행 제외
exclude_names = [
    "전국",
    "수도권",
    "지방",
    "4대광역시",
    "7개시도"
]

level_data = level_data[
    ~level_data["지역명"].isin(exclude_names)
].copy()

if level_data.empty:
    st.warning("선택한 조건에 해당하는 지역 데이터가 없습니다.")
    st.stop()


# =====================================================
# 6. 핵심 지표
# =====================================================

st.divider()
st.subheader("📊 전국 전월세 전환율 핵심 지표")

st.write(f"분석 기준: **{analysis_label}**")

average_rate = level_data["전환율"].mean()
maximum_rate = level_data["전환율"].max()
minimum_rate = level_data["전환율"].min()

max_region = level_data.loc[
    level_data["전환율"].idxmax(),
    "지역경로"
]

min_region = level_data.loc[
    level_data["전환율"].idxmin(),
    "지역경로"
]

c1, c2, c3, c4 = st.columns(4)

c1.metric("📌 지역 평균 전환율", f"{average_rate:.2f}%")
c2.metric("🔺 최고 전환율", f"{maximum_rate:.2f}%")
c3.metric("🔻 최저 전환율", f"{minimum_rate:.2f}%")
c4.metric("📍 분석 지역 수", f"{len(level_data)}개")

st.info(
    "지역 평균은 선택한 행정 단계에 포함된 지역별 전환율의 단순 평균입니다."
)


# =====================================================
# 7. 최고 및 최저 지역
# =====================================================

st.divider()
st.subheader("🏆 전환율 최고·최저 지역")

left, right = st.columns(2)

with left:
    st.markdown("### 🔺 전환율이 가장 높은 지역")
    st.metric(max_region, f"{maximum_rate:.2f}%")

with right:
    st.markdown("### 🔻 전환율이 가장 낮은 지역")
    st.metric(min_region, f"{minimum_rate:.2f}%")


# =====================================================
# 8. 지역별 TOP 10
# =====================================================

st.divider()
st.subheader("🥇 지역별 전환율 TOP 10")

top10 = (
    level_data.sort_values(
        "전환율",
        ascending=False
    )
    .head(10)
    .copy()
)

fig_top = px.bar(
    top10.sort_values("전환율"),
    x="전환율",
    y="지역경로",
    orientation="h",
    text="전환율",
    title=f"{analysis_label} 지역별 전환율 TOP 10",
    labels={
        "전환율": "전월세 전환율(%)",
        "지역경로": "지역"
    }
)

fig_top.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

fig_top.update_layout(
    template="plotly_white",
    height=480,
    showlegend=False
)

st.plotly_chart(
    fig_top,
    use_container_width=True
)


# =====================================================
# 9. 지역별 전환율 비교
# =====================================================

st.divider()
st.subheader("📊 지역별 전환율 비교")

all_regions = sorted(
    level_data["지역경로"].unique()
)

default_regions = (
    level_data.sort_values(
        "전환율",
        ascending=False
    )["지역경로"]
    .head(min(5, len(level_data)))
    .tolist()
)

selected_regions = st.multiselect(
    "비교할 지역을 선택하세요.",
    options=all_regions,
    default=default_regions
)

if selected_regions:

    compare_data = level_data[
        level_data["지역경로"].isin(selected_regions)
    ].copy()

    compare_fig = px.bar(
        compare_data.sort_values(
            "전환율",
            ascending=False
        ),
        x="지역경로",
        y="전환율",
        text="전환율",
        title="선택 지역 전환율 비교",
        labels={
            "지역경로": "지역",
            "전환율": "전월세 전환율(%)"
        }
    )

    compare_fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    compare_fig.update_layout(
        template="plotly_white",
        height=450,
        showlegend=False
    )

    st.plotly_chart(
        compare_fig,
        use_container_width=True
    )

else:
    st.warning("비교할 지역을 선택해 주세요.")


# =====================================================
# 10. 선택 지역의 월별 변화
# =====================================================

st.divider()
st.subheader("📈 선택 지역의 월별 전환율 변화")

region_options = sorted(
    year_data["지역경로"].unique()
)

selected_region = st.selectbox(
    "월별 추이를 확인할 지역",
    region_options
)

trend_data = year_data[
    year_data["지역경로"] == selected_region
].sort_values("날짜")

trend_fig = go.Figure()

trend_fig.add_trace(
    go.Scatter(
        x=trend_data["날짜"],
        y=trend_data["전환율"],
        mode="lines+markers",
        name="실제 전환율",
        line=dict(width=3),
        marker=dict(size=9)
    )
)

trend_fig.update_layout(
    title=f"{selected_region} 월별 전환율 변화",
    template="plotly_white",
    height=430,
    xaxis_title="월",
    yaxis_title="전월세 전환율(%)"
)

trend_fig.update_yaxes(ticksuffix="%")

st.plotly_chart(
    trend_fig,
    use_container_width=True
)


# =====================================================
# 11. 전월 대비 전환율 변화
# =====================================================

st.divider()
st.subheader("🔄 전월 대비 전환율 변화")

change_data = data[
    data["지역단계"] == selected_level
].copy()

change_data = change_data[
    ~change_data["지역명"].isin(exclude_names)
].copy()

change_data = change_data.sort_values(
    ["지역경로", "날짜"]
)

# 같은 지역의 이전 달 전환율
change_data["전월 전환율"] = (
    change_data.groupby("지역경로")["전환율"].shift(1)
)

# 전월 대비 변화량
change_data["전월 대비 변화"] = (
    change_data["전환율"]
    - change_data["전월 전환율"]
)

if selected_month == "연평균":

    change_view = (
        change_data[
            change_data["연도"] == selected_year
        ]
        .groupby(
            ["지역경로"],
            as_index=False
        )["전월 대비 변화"]
        .mean()
    )

else:

    change_view = change_data[
        (change_data["연도"] == selected_year)
        & (change_data["월"] == month_number)
    ][
        ["지역경로", "전월 대비 변화"]
    ].copy()

change_view["전월 대비 변화"] = pd.to_numeric(
    change_view["전월 대비 변화"],
    errors="coerce"
)

change_view = change_view.dropna(
    subset=["전월 대비 변화"]
)

if not change_view.empty:

    change_view = change_view.sort_values(
        "전월 대비 변화",
        ascending=False
    )

    increase, decrease = st.columns(2)

    # 상승 지역
    with increase:

        st.markdown("### 📈 전환율 상승 지역")

        increase_table = change_view.head(5)[
            ["지역경로", "전월 대비 변화"]
        ].copy()

        increase_table = increase_table.rename(
            columns={
                "지역경로": "지역",
                "전월 대비 변화": "전환율 변화(%p)"
            }
        )

        increase_table["전환율 변화(%p)"] = (
            increase_table["전환율 변화(%p)"].round(2)
        )

        st.dataframe(
            increase_table,
            use_container_width=True,
            hide_index=True
        )

    # 하락 지역
    with decrease:

        st.markdown("### 📉 전환율 하락 지역")

        decrease_table = (
            change_view.tail(5)
            .sort_values("전월 대비 변화")
            [["지역경로", "전월 대비 변화"]]
            .copy()
        )

        decrease_table = decrease_table.rename(
            columns={
                "지역경로": "지역",
                "전월 대비 변화": "전환율 변화(%p)"
            }
        )

        decrease_table["전환율 변화(%p)"] = (
            decrease_table["전환율 변화(%p)"].round(2)
        )

        st.dataframe(
            decrease_table,
            use_container_width=True,
            hide_index=True
        )

else:

    st.info(
        "선택한 조건에서 전월 대비 비교할 수 있는 데이터가 없습니다."
    )


# =====================================================
# 12. 전체 데이터 표
# =====================================================

st.divider()
st.subheader("📋 지역별 전월세 전환율 데이터")

# 원본 데이터에서 필요한 두 열만 새로 구성
# 기존 지역 열과 지역명 열이 중복되는 문제 방지
table_data = analysis_data[
    ["지역경로", "전환율"]
].copy()

# 새 데이터프레임을 만들고 열 이름을 각각 지정
table_data = pd.DataFrame({
    "지역": table_data["지역경로"].astype(str),
    "전월세 전환율(%)": pd.to_numeric(
        table_data["전환율"],
        errors="coerce"
    ).round(2)
})

table_data = table_data.sort_values(
    "전월세 전환율(%)",
    ascending=False
).reset_index(drop=True)

st.dataframe(
    table_data,
    use_container_width=True,
    hide_index=True
)


# =====================================================
# 13. CSV 다운로드
# =====================================================

st.divider()
st.subheader("📥 분석 결과 다운로드")

csv_download = table_data.to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="분석 결과 CSV 다운로드",
    data=csv_download,
    file_name="전월세_전환율_분석결과.csv",
    mime="text/csv"
)


# =====================================================
# 14. 분석 설명
# =====================================================

st.divider()
st.subheader("💡 전월세 전환율 분석이란?")

st.markdown("""
**① 지역별 분석**

지역마다 전월세 전환율이 어떻게 다른지 비교합니다.

**② 순위 분석**

전환율이 높은 지역과 낮은 지역을 확인합니다.

**③ 시계열 분석**

시간의 흐름에 따라 전환율이 어떻게 변하는지 확인합니다.

**④ 변화량 분석**

전월과 비교하여 전환율이 상승했는지 하락했는지 확인합니다.

**⑤ 데이터 기반 의사결정**

지역별 전환율의 차이를 확인하여 부동산 시장의 지역별 특징을 이해할 수 있습니다.

※ 전환율은 시장 상황, 금리, 정책 등에 따라 달라질 수 있습니다.
전환율만으로 특정 지역의 주거비 부담이나 투자 수익성을 단정할 수는 없습니다.
""")

st.caption(
    f"사용 데이터: {CSV_FILE.name} | 분석 연도: {selected_year}년"
)


import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 페이지 기본 설정
# ==========================================

st.set_page_config(
    page_title="서울 월별 기온 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 월별 기온 분석")
st.markdown("### 원하는 월을 선택하여 연도별 최고기온과 최저기온을 비교해 보세요!")

st.divider()

# ==========================================
# 2. CSV 파일 불러오기
# ==========================================

file_name = "extremum_20261109105046 (1).csv"
file_path = Path(__file__).parent / file_name

uploaded_file = st.file_uploader(
    "CSV 데이터 파일 업로드",
    type=["csv"]
)

try:
    if uploaded_file is not None:
        df = pd.read_csv(
            uploaded_file,
            encoding="cp949",
            skiprows=11,
            skipinitialspace=True
        )
    elif file_path.exists():
        df = pd.read_csv(
            file_path,
            encoding="cp949",
            skiprows=11,
            skipinitialspace=True
        )
    else:
        st.error("CSV 파일을 찾을 수 없습니다. 파일을 업로드해 주세요.")
        st.stop()

except UnicodeDecodeError:
    st.error("파일 인코딩을 확인해 주세요. 원본 파일은 CP949 형식이어야 합니다.")
    st.stop()

except Exception as e:
    st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

# ==========================================
# 3. 데이터 전처리
# ==========================================

df.columns = df.columns.str.strip()

# 필요한 컬럼 확인
required_columns = [
    "일시",
    "최고기온(℃)",
    "최저기온(℃)"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(f"필요한 컬럼이 없습니다: {missing_columns}")
    st.stop()

# 날짜 변환
df["일시"] = pd.to_datetime(
    df["일시"],
    format="%Y-%m",
    errors="coerce"
)

# 기온 숫자 변환
df["최고기온(℃)"] = pd.to_numeric(
    df["최고기온(℃)"],
    errors="coerce"
)

df["최저기온(℃)"] = pd.to_numeric(
    df["최저기온(℃)"],
    errors="coerce"
)

# 연도와 월 추출
df["연도"] = df["일시"].dt.year
df["월"] = df["일시"].dt.month

# 결측치 제거
df = df.dropna(
    subset=[
        "연도",
        "월",
        "최고기온(℃)",
        "최저기온(℃)"
    ]
).copy()

df["연도"] = df["연도"].astype(int)
df["월"] = df["월"].astype(int)

# ==========================================
# 4. 월 선택
# ==========================================

st.subheader("📅 분석할 월 선택")

selected_month = st.selectbox(
    "월을 선택하세요",
    options=list(range(1, 13)),
    format_func=lambda x: f"{x}월",
    index=0
)

# ==========================================
# 5. 선택한 월의 데이터 추출
# ==========================================

month_df = df[df["월"] == selected_month].copy()

# 연도별 최고기온과 최저기온
chart_df = (
    month_df.groupby("연도")
    .agg({
        "최고기온(℃)": "max",
        "최저기온(℃)": "min"
    })
    .reset_index()
    .sort_values("연도")
)

if chart_df.empty:
    st.warning("선택한 월의 데이터가 없습니다.")
    st.stop()

# ==========================================
# 6. 요약 정보
# ==========================================

st.subheader(f"📊 {selected_month}월 기온 분석 결과")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "분석 연도 수",
        f"{len(chart_df)}년"
    )

with col2:
    max_row = chart_df.loc[
        chart_df["최고기온(℃)"].idxmax()
    ]

    st.metric(
        "역대 최고기온",
        f"{max_row['최고기온(℃)']:.1f}℃",
        f"{int(max_row['연도'])}년"
    )

with col3:
    min_row = chart_df.loc[
        chart_df["최저기온(℃)"].idxmin()
    ]

    st.metric(
        "역대 최저기온",
        f"{min_row['최저기온(℃)']:.1f}℃",
        f"{int(min_row['연도'])}년"
    )

st.divider()

# ==========================================
# 7. 그래프 작성
# ==========================================

st.subheader("📈 월별 기온 분석")

fig = go.Figure()

# 최고기온 그래프 - 연두색
fig.add_trace(
    go.Scatter(
        x=chart_df["연도"],
        y=chart_df["최고기온(℃)"],
        mode="lines+markers",
        name="최고기온",
        line=dict(
            color="#90EE90",
            width=3
        ),
        marker=dict(
            size=7,
            color="#90EE90"
        ),
        hovertemplate=(
            "%{x}년<br>"
            "최고기온: %{y:.1f}℃"
            "<extra></extra>"
        )
    )
)

# 최저기온 그래프 - 하늘색
fig.add_trace(
    go.Scatter(
        x=chart_df["연도"],
        y=chart_df["최저기온(℃)"],
        mode="lines+markers",
        name="최저기온",
        line=dict(
            color="#87CEEB",
            width=3
        ),
        marker=dict(
            size=7,
            color="#87CEEB"
        ),
        hovertemplate=(
            "%{x}년<br>"
            "최저기온: %{y:.1f}℃"
            "<extra></extra>"
        )
    )
)

# 그래프 레이아웃
fig.update_layout(
    title={
        "text": f"{selected_month}월 월별 기온 분석",
        "x": 0.5,
        "xanchor": "center",
        "font": {
            "size": 24
        }
    },

    xaxis=dict(
        title="연도",
        showgrid=True,
        dtick=10
    ),

    yaxis=dict(
        title="온도(℃)",
        showgrid=True,
        zeroline=True
    ),

    legend=dict(
        title="기온 구분",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),

    hovermode="x unified",

    template="plotly_white",

    height=600
)

# 그래프 출력
st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================
# 8. 연도별 데이터 표
# ==========================================

with st.expander("📋 연도별 상세 기온 데이터 보기"):

    display_df = chart_df.copy()

    display_df.columns = [
        "연도",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# 9. 데이터 다운로드
# ==========================================

csv_data = chart_df.to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="📥 분석 데이터 CSV 다운로드",
    data=csv_data.encode("utf-8-sig"),
    file_name=f"서울_{selected_month}월_기온분석.csv",
    mime="text/csv"
)

# ==========================================
# 10. 안내 문구
# ==========================================

st.divider()

st.caption(
    "자료: 기상청 기상자료 | "
    "분석 기준: 선택한 월의 연도별 월간 최고기온 및 최저기온"
)

st.caption(
    "※ 자료가 존재하는 연도만 그래프에 표시됩니다."
)

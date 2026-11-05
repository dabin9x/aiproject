
import re
from pathlib import Path

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter

# --------------------------------------------------
# 은평구 연령별 인구 분석
# CSV는 pages 폴더의 상위 폴더에 위치
# --------------------------------------------------

st.set_page_config(
    page_title="은평구 연령별 인구 분석",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 은평구 연령별 인구 분석")
st.caption("행정구역 · 성별 · 연도를 선택해 연령별 인구를 분석하세요.")

# pages 폴더의 상위 폴더
PROJECT_DIR = Path(__file__).resolve().parent.parent

# CSV 파일 경로
DATA_FILE = PROJECT_DIR / "population.csv"


# --------------------------------------------------
# 한글 CSV 인코딩 처리
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
        "CSV 한글 인코딩을 확인할 수 없습니다."
    ) from last_error


# --------------------------------------------------
# 행정구역 이름 정리
# --------------------------------------------------

def clean_area_name(value):

    return re.sub(
        r"\s*\(\d+\)\s*$",
        "",
        str(value)
    ).strip()


# --------------------------------------------------
# 연령 순서 정렬
# --------------------------------------------------

def age_sort_key(age_label):

    if "100세" in age_label:
        return 100

    match = re.match(r"(\d+)", age_label)

    return int(match.group(1)) if match else 999


# --------------------------------------------------
# 연도와 성별에 맞는 열 찾기
# --------------------------------------------------

def find_age_columns(columns, year, gender):

    if gender == "전체":

        pattern = re.compile(
            rf"^{year}년_거주자_(\d+~\d+세|100세 이상)$"
        )

    else:

        gender_code = "남" if gender == "남성" else "여"

        pattern = re.compile(
            rf"^{year}년_{gender_code}_거주자_(\d+~\d+세|100세 이상)$"
        )

    age_columns = []

    for column in columns:

        match = pattern.match(str(column).strip())

        if match:

            age_columns.append(
                (match.group(1), column)
            )

    age_columns.sort(
        key=lambda item: age_sort_key(item[0])
    )

    return age_columns


# --------------------------------------------------
# CSV 파일 불러오기
# --------------------------------------------------

if not DATA_FILE.exists():

    st.error(
        "population.csv 파일을 찾을 수 없습니다.\n\n"
        f"파일 위치: {DATA_FILE}\n\n"
        "CSV 파일이 프로젝트 최상위 폴더에 있는지 확인하세요."
    )

    st.stop()


try:

    df, used_encoding = load_data(DATA_FILE)

except Exception as error:

    st.error(
        f"데이터를 불러오는 중 오류가 발생했습니다: {error}"
    )

    st.stop()


if "행정구역" not in df.columns:

    st.error("행정구역 열이 없습니다.")

    st.stop()


# --------------------------------------------------
# 행정구역 및 연도 추출
# --------------------------------------------------

df["행정구역_표시"] = (
    df["행정구역"].apply(clean_area_name)
)

area_options = (
    df["행정구역_표시"].dropna().tolist()
)

years = sorted({

    int(match.group(1))

    for column in df.columns

    if (match := re.match(
        r"^(\d{4})년_",
        str(column).strip()
    ))

})


if not area_options or not years:

    st.error("행정구역 또는 연도 정보를 찾지 못했습니다.")

    st.stop()


# --------------------------------------------------
# 선택 메뉴
# --------------------------------------------------

st.subheader("🔎 분석 조건 선택")

col1, col2, col3 = st.columns(3)

with col1:

    selected_area = st.selectbox(
        "행정구역",
        area_options
    )

with col2:

    selected_gender = st.selectbox(
        "성별",
        ["전체", "남성", "여성"]
    )

with col3:

    selected_year = st.selectbox(
        "연도",
        years,
        index=len(years) - 1,
        format_func=lambda year: f"{year}년"
    )


# --------------------------------------------------
# 선택한 데이터 추출
# --------------------------------------------------

selected_rows = df[
    df["행정구역_표시"] == selected_area
]

if selected_rows.empty:

    st.error("선택한 행정구역 데이터가 없습니다.")

    st.stop()


selected_row = selected_rows.iloc[0]


age_columns = find_age_columns(
    df.columns,
    selected_year,
    selected_gender
)


if not age_columns:

    st.warning("해당 연령별 데이터를 찾지 못했습니다.")

    st.stop()


# --------------------------------------------------
# 연령별 인구 데이터 생성
# --------------------------------------------------

ages = []
populations = []

for age_label, column in age_columns:

    value = pd.to_numeric(
        str(selected_row[column])
        .replace(",", "")
        .strip(),
        errors="coerce"
    )

    if pd.notna(value):

        ages.append(age_label)

        populations.append(int(value))


if not populations:

    st.warning("표시할 인구 데이터가 없습니다.")

    st.stop()


chart_df = pd.DataFrame({

    "나이": ages,

    "인구수": populations

})


# --------------------------------------------------
# 핵심 통계
# --------------------------------------------------

metric1, metric2, metric3 = st.columns(3)

with metric1:

    st.metric(
        "선택 행정구역",
        selected_area
    )

with metric2:

    st.metric(
        "연령별 인구 합계",
        f"{sum(populations):,}명"
    )

with metric3:

    max_index = chart_df["인구수"].idxmax()

    st.metric(
        "인구가 가장 많은 연령대",
        chart_df.loc[max_index, "나이"],
        f'{chart_df.loc[max_index, "인구수"]:,}명'
    )


# --------------------------------------------------
# 핫핑크 꺾은선 그래프
# --------------------------------------------------

st.subheader(
    f"📈 {selected_area} · {selected_gender} · "
    f"{selected_year}년 연령별 인구"
)

# 한글 폰트 설정
plt.rcParams["font.family"] = "Noto Sans CJK KR"

plt.rcParams["axes.unicode_minus"] = False


fig, ax = plt.subplots(figsize=(12, 6))

hot_pink = "#FF1493"


ax.plot(
    chart_df["나이"],
    chart_df["인구수"],
    color=hot_pink,
    linewidth=3,
    marker="o",
    markersize=7,
    markerfacecolor=hot_pink,
    markeredgecolor="white",
    markeredgewidth=1.2
)


# 각 연령대 인구수 표시
for age, population in zip(
    chart_df["나이"],
    chart_df["인구수"]
):

    ax.annotate(
        f"{population:,}",
        (age, population),
        textcoords="offset points",
        xytext=(0, 9),
        ha="center",
        fontsize=8,
        color="#A3155D"
    )


ax.set_xlabel(
    "나이",
    fontsize=12,
    labelpad=10
)

ax.set_ylabel(
    "인구수 (명)",
    fontsize=12,
    labelpad=10
)

ax.set_title(
    f"{selected_area} {selected_gender} "
    f"{selected_year}년 연령별 인구",
    fontsize=15,
    pad=18
)


# 가로축 연령대
ax.set_xticks(range(len(chart_df)))

ax.set_xticklabels(chart_df["나이"])


# 세로축 10만 명 단위 구분선
max_population = max(populations)

y_max = max(
    100_000,
    ((max_population // 100_000) + 1) * 100_000
)

ax.set_ylim(0, y_max)

ax.yaxis.set_major_locator(
    MultipleLocator(100_000)
)

ax.yaxis.set_major_formatter(
    FuncFormatter(
        lambda value, position: f"{int(value):,}"
    )
)


# 가로 구분선 디자인
ax.grid(
    axis="y",
    which="major",
    linestyle="--",
    linewidth=0.9,
    alpha=0.6,
    color="#E6A0C4"
)

ax.grid(axis="x", visible=False)

ax.set_axisbelow(True)


# 테두리 정리
for spine in ["top", "right"]:

    ax.spines[spine].set_visible(False)


fig.tight_layout()

st.pyplot(
    fig,
    use_container_width=True
)

plt.close(fig)


st.caption(
    "※ 가로축은 나이(연령대), 세로축은 인구수입니다. "
    "10만 명 단위 구분선은 세로축에 적용했습니다."
)


# --------------------------------------------------
# 데이터 표
# --------------------------------------------------

with st.expander("📋 연령별 인구 데이터 표 보기"):

    display_df = chart_df.copy()

    display_df["인구수"] = display_df["인구수"].map(
        lambda value: f"{value:,}명"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# 데이터 정보
# --------------------------------------------------

with st.expander("ℹ️ 데이터 및 인코딩 정보"):

    missing_count = int(
        df.isna().sum().sum()
    )

    st.write(f"CSV 위치: {DATA_FILE}")

    st.write(f"사용 인코딩: {used_encoding}")

    st.write(
        f"데이터 크기: {df.shape[0]}행 × {df.shape[1]-1}열"
    )

    st.write(
        f"결측치: {missing_count:,}개"
    )

    st.write(
        "한글 글꼴: Noto Sans CJK KR"
    )

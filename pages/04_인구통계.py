import re
from pathlib import Path

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import MultipleLocator, FuncFormatter


# ==================================================
# 1. 기본 설정
# ==================================================

st.set_page_config(
    page_title="은평구 연령별 인구 분석",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 은평구 연령별 인구 분석")
st.caption("은평구의 남녀 인구와 연령별 인구 구조를 분석합니다.")

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "population.csv"


# ==================================================
# 2. 한글 폰트 설정
# ==================================================

def set_korean_font():

    possible_fonts = [
        Path("/usr/share/fonts/truetype/nanum/NanumGothic.ttf"),
        Path("/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"),
    ]

    for font_path in possible_fonts:

        if font_path.exists():

            try:
                font_manager.fontManager.addfont(str(font_path))

                font_name = font_manager.FontProperties(
                    fname=str(font_path)
                ).get_name()

                plt.rcParams["font.family"] = font_name
                plt.rcParams["axes.unicode_minus"] = False

                return font_name

            except Exception:
                continue

    installed_fonts = {
        font.name
        for font in font_manager.fontManager.ttflist
    }

    for candidate in [
        "NanumGothic",
        "Noto Sans CJK KR",
        "Malgun Gothic",
        "AppleGothic",
    ]:

        if candidate in installed_fonts:

            plt.rcParams["font.family"] = candidate
            plt.rcParams["axes.unicode_minus"] = False

            return candidate

    plt.rcParams["axes.unicode_minus"] = False

    return "기본 글꼴"


font_name = set_korean_font()


# ==================================================
# 3. CSV 불러오기
# ==================================================

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


if not DATA_FILE.exists():

    st.error(
        f"population.csv 파일을 찾을 수 없습니다.\n\n"
        f"파일 위치: {DATA_FILE}"
    )

    st.stop()


try:

    df, used_encoding = load_data(str(DATA_FILE))

except Exception as error:

    st.error(f"데이터 불러오기 오류: {error}")

    st.stop()


if "행정구역" not in df.columns:

    st.error("CSV에 행정구역 열이 없습니다.")

    st.stop()


# ==================================================
# 4. 데이터 정리
# ==================================================

def clean_area_name(value):

    return re.sub(
        r"\s*\(\d+\)\s*$",
        "",
        str(value)
    ).strip()


def age_sort_key(age):

    if "100세" in age:
        return 100

    match = re.match(r"(\d+)", age)

    return int(match.group(1)) if match else 999


def find_age_columns(columns, year, gender):

    gender_code = "남" if gender == "남성" else "여"

    pattern = re.compile(
        rf"^{year}년_{gender_code}_거주자_(\d+~\d+세|100세 이상)$"
    )

    result = []

    for column in columns:

        match = pattern.match(str(column).strip())

        if match:

            result.append(
                (match.group(1), column)
            )

    result.sort(
        key=lambda item: age_sort_key(item[0])
    )

    return result


def to_number(value):

    return pd.to_numeric(
        str(value).replace(",", "").strip(),
        errors="coerce"
    )


df["행정구역_표시"] = (
    df["행정구역"].apply(clean_area_name)
)


# 연도 추출

years = sorted({

    int(match.group(1))

    for column in df.columns

    if (match := re.match(
        r"^(\d{4})년_",
        str(column).strip()
    ))

})


if not years:

    st.error("연도별 데이터를 찾을 수 없습니다.")

    st.stop()


# 행정동 추출

dong_df = df[
    df["행정구역_표시"].str.endswith("동", na=False)
].copy()

if dong_df.empty:

    st.error(
        "행정동 데이터를 찾지 못했습니다. "
        "CSV의 행정구역 이름을 확인해 주세요."
    )

    st.stop()


area_options = dong_df["행정구역_표시"].tolist()


# ==================================================
# 5. 분석 조건 선택
# ==================================================

st.subheader("🔎 분석 조건 선택")

col1, col2 = st.columns(2)

with col1:

    selected_area = st.selectbox(
        "행정동 선택",
        area_options
    )

with col2:

    selected_year = st.selectbox(
        "분석 연도",
        years,
        index=len(years) - 1,
        format_func=lambda y: f"{y}년"
    )


# 선택 행정동

selected_row = dong_df[
    dong_df["행정구역_표시"] == selected_area
].iloc[0]


male_columns = find_age_columns(
    df.columns,
    selected_year,
    "남성"
)

female_columns = find_age_columns(
    df.columns,
    selected_year,
    "여성"
)


if not male_columns or not female_columns:

    st.error(
        "남성 또는 여성 연령별 열을 찾지 못했습니다. "
        "CSV의 열 이름을 확인해 주세요."
    )

    st.stop()


# ==================================================
# 6. 남녀 연령별 데이터 만들기
# ==================================================

male_data = {}
female_data = {}

for age, column in male_columns:

    male_data[age] = to_number(
        selected_row[column]
    )

for age, column in female_columns:

    female_data[age] = to_number(
        selected_row[column]
    )


common_ages = sorted(
    set(male_data) & set(female_data),
    key=age_sort_key
)

if not common_ages:

    st.error("남녀 공통 연령대 데이터를 찾지 못했습니다.")

    st.stop()


chart_df = pd.DataFrame({

    "연령대": common_ages,

    "남성": [
        male_data[age] for age in common_ages
    ],

    "여성": [
        female_data[age] for age in common_ages
    ]

})

chart_df = chart_df.fillna(0)

chart_df["남성"] = chart_df["남성"].astype(int)
chart_df["여성"] = chart_df["여성"].astype(int)


# ==================================================
# 7. 핵심 통계
# ==================================================

male_total = int(chart_df["남성"].sum())
female_total = int(chart_df["여성"].sum())

total_population = male_total + female_total

male_ratio = (
    male_total / total_population * 100
    if total_population > 0 else 0
)

female_ratio = (
    female_total / total_population * 100
    if total_population > 0 else 0
)

total_by_age = (
    chart_df["남성"] + chart_df["여성"]
)

max_age_index = total_by_age.idxmax()

max_age = chart_df.loc[max_age_index, "연령대"]

max_age_population = int(
    total_by_age.loc[max_age_index]
)


st.subheader("📊 주요 인구 통계")

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "전체 인구",
    f"{total_population:,}명"
)

m2.metric(
    "남성 인구",
    f"{male_total:,}명"
)

m3.metric(
    "여성 인구",
    f"{female_total:,}명"
)

m4.metric(
    "인구가 가장 많은 연령대",
    max_age,
    f"{max_age_population:,}명"
)


st.caption(
    f"남성 비율 {male_ratio:.1f}% · "
    f"여성 비율 {female_ratio:.1f}%"
)


# ==================================================
# 8. 남녀 연령별 꺾은선 그래프
# ==================================================

st.subheader(
    f"📈 {selected_area} {selected_year}년 남녀 연령별 인구"
)

fig, ax = plt.subplots(figsize=(13, 6))

x = list(range(len(chart_df)))

# 남성 핑크색

ax.plot(
    x,
    chart_df["남성"],
    color="#FF1493",
    linewidth=3,
    marker="o",
    markersize=6,
    label="남성"
)

# 여성 초록색

ax.plot(
    x,
    chart_df["여성"],
    color="#159947",
    linewidth=3,
    marker="o",
    markersize=6,
    label="여성"
)

ax.set_xticks(x)

ax.set_xticklabels(
    chart_df["연령대"]
)

ax.set_xlabel("연령대")
ax.set_ylabel("인구수 (명)")

ax.set_title(
    f"{selected_area} {selected_year}년 남녀 연령별 인구",
    fontsize=15,
    pad=18
)

ax.yaxis.set_major_formatter(
    FuncFormatter(
        lambda value, position: f"{int(value):,}"
    )
)

ax.grid(
    axis="y",
    linestyle="--",
    alpha=0.5
)

ax.grid(
    axis="x",
    visible=False
)

ax.legend()

for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

fig.tight_layout()

st.pyplot(
    fig,
    use_container_width=True
)

plt.close(fig)


# ==================================================
# 9. 남녀 인구 비율 그래프
# ==================================================

st.subheader("🥧 남녀 인구 비율")

fig2, ax2 = plt.subplots(figsize=(7, 5))

if total_population > 0:

    ax2.pie(
        [male_total, female_total],
        labels=["남성", "여성"],
        colors=["#FF1493", "#159947"],
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={
            "edgecolor": "white",
            "linewidth": 2
        }
    )

    ax2.set_title(
        f"{selected_area} 남녀 인구 비율"
    )

    st.pyplot(
        fig2,
        use_container_width=True
    )

else:

    st.info("인구 데이터가 없어 비율을 표시할 수 없습니다.")

plt.close(fig2)


# ==================================================
# 10. 연령대 선택 후 행정동 순위 분석
# ==================================================

st.divider()

st.header("🏆 연령대별 인구가 가장 많은 행정동")

st.write(
    "원하는 연령대를 선택하면 해당 연령대의 인구가 "
    "많은 행정동을 순위별로 보여줍니다."
)


age_options = common_ages

selected_age = st.selectbox(
    "분석할 연령대 선택",
    age_options,
    key="ranking_age"
)


ranking_gender = st.radio(
    "인구 기준",
    ["남녀 합계", "남성", "여성"],
    horizontal=True
)


# 선택 연령대의 남녀 열 찾기

male_age_column = dict(male_columns).get(selected_age)
female_age_column = dict(female_columns).get(selected_age)


ranking_data = []

for _, row in dong_df.iterrows():

    male_value = (
        to_number(row[male_age_column])
        if male_age_column else 0
    )

    female_value = (
        to_number(row[female_age_column])
        if female_age_column else 0
    )

    male_value = (
        int(male_value)
        if pd.notna(male_value) else 0
    )

    female_value = (
        int(female_value)
        if pd.notna(female_value) else 0
    )

    if ranking_gender == "남성":

        population = male_value

    elif ranking_gender == "여성":

        population = female_value

    else:

        population = male_value + female_value

    ranking_data.append({

        "행정동": row["행정구역_표시"],

        "인구수": population

    })


ranking_df = pd.DataFrame(ranking_data)

ranking_df = ranking_df.sort_values(
    "인구수",
    ascending=False
).reset_index(drop=True)

ranking_df.index = ranking_df.index + 1

top10 = ranking_df.head(10)


if not top10.empty:

    winner = top10.iloc[0]

    st.success(
        f"🏆 {selected_age} {ranking_gender} 인구가 "
        f"가장 많은 행정동은 "
        f"**{winner['행정동']}**입니다. "
        f"({winner['인구수']:,}명)"
    )


    fig3, ax3 = plt.subplots(figsize=(12, 6))

    colors = [
        "#FF1493" if i == 0 else "#F3A5CE"
        for i in range(len(top10))
    ]

    ax3.barh(
        top10["행정동"].iloc[::-1],
        top10["인구수"].iloc[::-1],
        color=colors[::-1]
    )

    ax3.set_title(
        f"{selected_year}년 {selected_age} "
        f"{ranking_gender} 인구 상위 10개 행정동",
        fontsize=14
    )

    ax3.set_xlabel("인구수 (명)")

    ax3.xaxis.set_major_formatter(
        FuncFormatter(
            lambda value, position: f"{int(value):,}"
        )
    )

    ax3.grid(
        axis="x",
        linestyle="--",
        alpha=0.4
    )

    ax3.set_axisbelow(True)

    fig3.tight_layout()

    st.pyplot(
        fig3,
        use_container_width=True
    )

    plt.close(fig3)


    display_ranking = top10.copy()

    display_ranking.index = range(1, len(display_ranking) + 1)

    display_ranking["인구수"] = (
        display_ranking["인구수"].map(
            lambda value: f"{value:,}명"
        )
    )

    st.dataframe(
        display_ranking,
        use_container_width=True
    )


# ==================================================
# 11. 선택 행정동의 연령대별 인구 분포
# ==================================================

st.divider()

st.header("👨‍👩‍👧‍👦 우리 동네 연령 구조")

st.write(
    "선택한 행정동의 연령대별 남녀 인구를 합쳐 "
    "어떤 연령층이 많은지 확인할 수 있습니다."
)


age_chart_df = chart_df.copy()

age_chart_df["전체"] = (
    age_chart_df["남성"] + age_chart_df["여성"]
)

fig4, ax4 = plt.subplots(figsize=(13, 5))

ax4.bar(
    age_chart_df["연령대"],
    age_chart_df["전체"],
    color="#B58AE5",
    edgecolor="white"
)

ax4.set_title(
    f"{selected_area} 연령대별 전체 인구"
)

ax4.set_xlabel("연령대")
ax4.set_ylabel("인구수 (명)")

ax4.yaxis.set_major_formatter(
    FuncFormatter(
        lambda value, position: f"{int(value):,}"
    )
)

ax4.grid(
    axis="y",
    linestyle="--",
    alpha=0.4
)

ax4.set_axisbelow(True)

fig4.tight_layout()

st.pyplot(
    fig4,
    use_container_width=True
)

plt.close(fig4)


# ==================================================
# 12. 연령별 데이터 표
# ==================================================

with st.expander("📋 남녀 연령별 데이터 표 보기"):

    display_df = chart_df.copy()

    for column in ["남성", "여성"]:

        display_df[column] = (
            display_df[column].map(
                lambda value: f"{value:,}명"
            )
        )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


with st.expander("🏆 전체 행정동 연령대별 순위표"):

    full_ranking = ranking_df.copy()

    full_ranking.index = range(
        1,
        len(full_ranking) + 1
    )

    full_ranking["인구수"] = (
        full_ranking["인구수"].map(
            lambda value: f"{value:,}명"
        )
    )

    st.dataframe(
        full_ranking,
        use_container_width=True
    )


# ==================================================
# 13. 데이터 정보
# ==================================================

with st.expander("ℹ️ 데이터 및 글꼴 정보"):

    st.write(f"CSV 파일: {DATA_FILE}")

    st.write(f"사용 인코딩: {used_encoding}")

    st.write(
        f"데이터 크기: {df.shape[0]}행 × {df.shape[1]}열"
    )

    st.write(
        f"결측치: {int(df.isna().sum().sum()):,}개"
    )

    st.write(
        f"그래프 글꼴: {font_name}"
    )

    st.write(
        "분석 대상: 행정동 데이터"
    )

st.caption(
    "🌸 은평구 연령별 인구 분석 | "
    "CSV에 수록된 연도별·성별·연령별 데이터를 활용합니다."
)


import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report


# ==================================================
# 1. 페이지 설정
# ==================================================

st.set_page_config(
    page_title="붓꽃 품종 예측 시스템",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃(Iris) 품종 예측 시스템")

st.markdown("""
꽃잎의 길이와 너비를 입력하고,
3가지 머신러닝 알고리즘 중 하나를 선택하여
붓꽃의 품종을 예측해 보세요!
""")

st.divider()


# ==================================================
# 2. 데이터 불러오기
# ==================================================

@st.cache_data
def load_data():

    current_dir = Path(__file__).resolve().parent

    file_candidates = [
        current_dir / "Iris.csv",
        current_dir.parent / "Iris.csv"
    ]

    file_path = None

    for path in file_candidates:
        if path.exists():
            file_path = path
            break

    if file_path is None:
        raise FileNotFoundError(
            "Iris.csv 파일을 찾을 수 없습니다."
        )

    data = None

    for encoding in [
        "cp949",
        "utf-8-sig",
        "euc-kr",
        "utf-8"
    ]:

        try:
            data = pd.read_csv(
                file_path,
                encoding=encoding
            )
            break

        except UnicodeDecodeError:
            continue

    if data is None:
        raise ValueError("CSV 인코딩을 확인해주세요.")

    required_columns = [
        "꽃잎 길이",
        "꽃잎 너비",
        "품종"
    ]

    for col in required_columns:

        if col not in data.columns:
            raise ValueError(
                f"'{col}' 컬럼이 CSV 파일에 없습니다."
            )

    data = data[required_columns].copy()

    data["꽃잎 길이"] = pd.to_numeric(
        data["꽃잎 길이"],
        errors="coerce"
    )

    data["꽃잎 너비"] = pd.to_numeric(
        data["꽃잎 너비"],
        errors="coerce"
    )

    data = data.dropna()

    return data


try:
    df = load_data()

except Exception as e:

    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


FEATURES = [
    "꽃잎 길이",
    "꽃잎 너비"
]

TARGET = "품종"

X = df[FEATURES]
y = df[TARGET]


# ==================================================
# 3. 입력 범위 설정
# ==================================================

min_length = float(df["꽃잎 길이"].min())
max_length = float(df["꽃잎 길이"].max())

min_width = float(df["꽃잎 너비"].min())
max_width = float(df["꽃잎 너비"].max())


# ==================================================
# 4. 데이터 기본 정보
# ==================================================

st.subheader("📊 데이터 기본 정보")

col1, col2, col3 = st.columns(3)

col1.metric(
    "전체 데이터",
    f"{len(df)}개"
)

col2.metric(
    "붓꽃 품종",
    f"{df[TARGET].nunique()}종"
)

col3.metric(
    "분석 변수",
    "2개"
)

with st.expander("품종별 데이터 개수 확인"):

    st.dataframe(
        df[TARGET].value_counts().rename("데이터 개수"),
        use_container_width=True
    )

st.divider()


# ==================================================
# 5. 머신러닝 알고리즘 설명
# ==================================================

st.subheader("🤖 머신러닝 알고리즘 선택")

algorithm_descriptions = {

    "Random Forest": {
        "설명": """
        여러 개의 의사결정나무를 만들어 각각 예측한 뒤
        다수결 방식으로 최종 품종을 결정합니다.

        **특징**
        - 여러 나무의 예측 결과를 종합합니다.
        - 복잡한 데이터 분류에 유용합니다.
        - 여러 알고리즘 중 비교적 안정적인 결과를 기대할 수 있습니다.

        **설정:** 의사결정나무 200개 사용
        """,
        "장점": "여러 모델의 결과를 종합하여 안정적인 분류 가능",
        "단점": "단일 의사결정나무보다 결과 해석이 복잡함"
    },

    "Decision Tree": {
        "설명": """
        꽃잎 길이와 너비를 기준으로 여러 조건을 만들고
        조건에 따라 품종을 분류합니다.

        **특징**
        - 조건에 따른 분류 과정을 이해하기 쉽습니다.
        - 나무 형태로 분류 과정을 표현할 수 있습니다.
        - 데이터에 지나치게 맞춰질 수 있습니다.

        **설정:** 최대 깊이 5
        """,
        "장점": "분류 원리를 직관적으로 이해하기 쉬움",
        "단점": "학습 데이터에 과적합될 가능성이 있음"
    },

    "KNN": {
        "설명": """
        새로 입력한 꽃잎 크기와 가까운 기존 데이터
        5개를 찾아 주변 데이터의 품종을 비교합니다.

        **특징**
        - 가까운 데이터의 품종을 참고합니다.
        - 거리 계산을 이용합니다.
        - 입력 데이터의 주변에 어떤 품종이 많은지가 중요합니다.

        **설정:** 이웃 데이터 5개, 표준화 적용
        """,
        "장점": "주변 데이터와 비교하는 원리를 이해하기 쉬움",
        "단점": "데이터가 많아지면 예측 계산이 느려질 수 있음"
    }
}


algorithm = st.selectbox(
    "사용할 분류 알고리즘을 선택하세요.",
    [
        "Random Forest",
        "Decision Tree",
        "KNN"
    ]
)

selected_info = algorithm_descriptions[algorithm]

st.info(
    f"**선택한 알고리즘: {algorithm}**\n\n"
    + selected_info["설명"]
)

with st.expander("알고리즘 장단점 자세히 보기"):

    st.write("**장점**")
    st.write(selected_info["장점"])

    st.write("**단점**")
    st.write(selected_info["단점"])


# ==================================================
# 6. 알고리즘 모델 생성 함수
# ==================================================

def create_model(name):

    if name == "Random Forest":

        return RandomForestClassifier(
            n_estimators=200,
            max_depth=5,
            random_state=42,
            class_weight="balanced"
        )

    elif name == "Decision Tree":

        return DecisionTreeClassifier(
            max_depth=5,
            random_state=42,
            class_weight="balanced"
        )

    elif name == "KNN":

        return Pipeline([
            ("scaler", StandardScaler()),
            (
                "model",
                KNeighborsClassifier(
                    n_neighbors=5
                )
            )
        ])


# ==================================================
# 7. 모델 학습 및 평가
# ==================================================

@st.cache_resource
def train_model(name, data):

    X_data = data[FEATURES]
    y_data = data[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X_data,
        y_data,
        test_size=0.2,
        random_state=42,
        stratify=y_data
    )

    # 테스트용 모델
    evaluation_model = create_model(name)

    evaluation_model.fit(
        X_train,
        y_train
    )

    predictions = evaluation_model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    report = classification_report(
        y_test,
        predictions,
        zero_division=0
    )

    # 최종 예측용 모델은 전체 데이터로 다시 학습
    final_model = create_model(name)

    final_model.fit(
        X_data,
        y_data
    )

    return (
        final_model,
        accuracy,
        report
    )


model, accuracy, report = train_model(
    algorithm,
    df
)


# ==================================================
# 8. 모델 평가 결과
# ==================================================

st.subheader("📈 선택한 알고리즘의 성능")

col1, col2 = st.columns(2)

col1.metric(
    "알고리즘",
    algorithm
)

col2.metric(
    "테스트 데이터 정확도",
    f"{accuracy * 100:.2f}%"
)

st.caption(
    "전체 데이터의 20%를 테스트용으로 분리하여 "
    "나머지 80%로 학습한 뒤 정확도를 평가합니다."
)

with st.expander("상세 모델 평가 결과"):

    st.text(report)


st.divider()


# ==================================================
# 9. 사용자 입력
# ==================================================

st.subheader("✏️ 꽃잎 크기 입력하기")

st.info(
    f"""
    📌 Iris.csv의 실제 데이터 범위입니다.

    - 꽃잎 길이: {min_length} ~ {max_length} cm
    - 꽃잎 너비: {min_width} ~ {max_width} cm

    입력 범위를 확인하고 값을 입력해주세요.
    """
)

col1, col2 = st.columns(2)

with col1:

    petal_length = st.number_input(
        "🌷 꽃잎 길이 (cm)",
        min_value=min_length,
        max_value=max_length,
        value=1.5,
        step=0.1,
        format="%.1f"
    )

with col2:

    petal_width = st.number_input(
        "🌷 꽃잎 너비 (cm)",
        min_value=min_width,
        max_value=max_width,
        value=0.3,
        step=0.1,
        format="%.1f"
    )


# ==================================================
# 10. 품종 예측
# ==================================================

if st.button(
    "🌸 붓꽃 품종 예측하기",
    type="primary",
    use_container_width=True
):

    input_data = pd.DataFrame(
        [[petal_length, petal_width]],
        columns=FEATURES
    )

    predicted_species = model.predict(
        input_data
    )[0]

    probabilities = model.predict_proba(
        input_data
    )[0]

    probability_df = pd.DataFrame({

        "품종": model.classes_,

        "예측 확률": probabilities * 100

    }).sort_values(
        "예측 확률",
        ascending=False
    )

    st.session_state["result"] = {
        "algorithm": algorithm,
        "species": predicted_species,
        "probabilities": probability_df,
        "length": petal_length,
        "width": petal_width
    }


# ==================================================
# 11. 예측 결과 출력
# ==================================================

if "result" in st.session_state:

    result = st.session_state["result"]

    if result["algorithm"] != algorithm:

        st.warning(
            "알고리즘이 변경되었습니다. "
            "새 알고리즘으로 다시 예측해주세요."
        )

    else:

        predicted_species = result["species"]
        probability_df = result["probabilities"]

        petal_length = result["length"]
        petal_width = result["width"]

        st.divider()

        st.subheader("🎯 붓꽃 품종 예측 결과")

        st.success(
            f"예측 결과: {predicted_species} 🌸"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "사용 알고리즘",
            algorithm
        )

        col2.metric(
            "꽃잎 길이",
            f"{petal_length:.1f} cm"
        )

        col3.metric(
            "꽃잎 너비",
            f"{petal_width:.1f} cm"
        )


        # ------------------------------------------
        # 품종별 예측 확률
        # ------------------------------------------

        st.subheader("📊 품종별 예측 확률")

        fig_prob = go.Figure()

        fig_prob.add_trace(
            go.Bar(
                x=probability_df["예측 확률"],
                y=probability_df["품종"],
                orientation="h",
                text=[
                    f"{v:.1f}%"
                    for v in probability_df["예측 확률"]
                ],
                textposition="auto",
                marker_color=[
                    "#2E8B57"
                    if name == predicted_species
                    else "#82AADD"
                    for name in probability_df["품종"]
                ]
            )
        )

        fig_prob.update_layout(
            xaxis_title="예측 확률 (%)",
            yaxis_title="붓꽃 품종",
            xaxis=dict(range=[0, 100]),
            height=300,
            showlegend=False
        )

        st.plotly_chart(
            fig_prob,
            use_container_width=True
        )


        # ------------------------------------------
        # 분류 영역 그래프
        # ------------------------------------------

        st.divider()

        st.subheader("🗺️ 품종별 분류 영역 시각화")

        st.markdown("""
        **그래프 읽는 방법**

        - 파란색 영역: Setosa
        - 주황색 영역: Versicolor
        - 보라색 영역: Virginica
        - 초록색 별 ★: 사용자가 입력한 데이터

        배경색은 선택한 머신러닝 알고리즘이
        해당 위치를 어떤 품종으로 분류하는지 보여줍니다.
        """)

        x_range = np.linspace(
            min_length - 0.1,
            max_length + 0.1,
            180
        )

        y_range = np.linspace(
            min_width - 0.1,
            max_width + 0.1,
            180
        )

        xx, yy = np.meshgrid(
            x_range,
            y_range
        )

        grid_data = pd.DataFrame({

            "꽃잎 길이": xx.ravel(),

            "꽃잎 너비": yy.ravel()

        })

        grid_predictions = model.predict(
            grid_data
        )

        class_names = list(model.classes_)

        class_mapping = {
            name: index
            for index, name in enumerate(class_names)
        }

        zz = np.array([
            class_mapping[name]
            for name in grid_predictions
        ]).reshape(xx.shape)

        colors = [
            "#9CC9F0",
            "#F8C88B",
            "#C5A5E8"
        ]

        colorscale = []

        for i, color in enumerate(colors):

            left = i / 3
            right = (i + 1) / 3

            colorscale.append([left, color])
            colorscale.append([right - 0.0001, color])

        fig = go.Figure()

        # 분류 영역 배경
        fig.add_trace(
            go.Heatmap(
                x=x_range,
                y=y_range,
                z=zz,
                colorscale=colorscale,
                zmin=-0.5,
                zmax=2.5,
                showscale=False,
                opacity=0.55,
                hoverinfo="skip"
            )
        )

        # 기존 품종 데이터
        species_colors = {
            class_names[0]: "#2678C8",
            class_names[1]: "#E58A24",
            class_names[2]: "#8E5AC8"
        }

        for species in class_names:

            species_data = df[
                df[TARGET] == species
            ]

            fig.add_trace(
                go.Scatter(
                    x=species_data["꽃잎 길이"],
                    y=species_data["꽃잎 너비"],
                    mode="markers",
                    name=species,
                    marker=dict(
                        size=8,
                        color=species_colors[species],
                        opacity=0.8,
                        line=dict(
                            width=0.5,
                            color="white"
                        )
                    )
                )
            )

        # 사용자 입력값
        fig.add_trace(
            go.Scatter(
                x=[petal_length],
                y=[petal_width],
                mode="markers+text",
                name="사용자 입력값",
                text=["내 입력값 ★"],
                textposition="top center",
                marker=dict(
                    symbol="star",
                    size=24,
                    color="#00A651",
                    line=dict(
                        color="darkgreen",
                        width=2
                    )
                )
            )
        )

        fig.update_layout(
            title=f"{algorithm} 품종 분류 영역",
            xaxis_title="꽃잎 길이 (cm)",
            yaxis_title="꽃잎 너비 (cm)",
            height=650,
            template="plotly_white",
            legend_title="범례"
        )

        fig.update_xaxes(
            range=[
                min_length - 0.2,
                max_length + 0.2
            ]
        )

        fig.update_yaxes(
            range=[
                min_width - 0.2,
                max_width + 0.2
            ]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


        # ------------------------------------------
        # 분류 이유 설명
        # ------------------------------------------

        st.divider()

        st.subheader("🔍 왜 이 품종으로 분류되었을까요?")

        st.write(
            f"""
            선택한 알고리즘은 **{algorithm}**입니다.

            사용자가 입력한 값은 다음과 같습니다.

            - 꽃잎 길이: {petal_length:.1f} cm
            - 꽃잎 너비: {petal_width:.1f} cm

            그래프에서 초록색 별이 위치한 배경 영역은
            **{predicted_species}**로 분류되는 영역입니다.

            모델은 입력값을 기존 학습 데이터와 비교하고
            선택한 알고리즘의 분류 규칙에 따라
            {predicted_species} 품종으로 예측했습니다.
            """
        )

        st.markdown("### 품종별 예측 확률 비교")

        for _, row in probability_df.iterrows():

            species = row["품종"]
            probability = row["예측 확률"]

            st.write(
                f"**{species} : {probability:.1f}%**"
            )

            st.progress(
                float(probability / 100)
            )


        # ------------------------------------------
        # 변수 중요도
        # ------------------------------------------

        st.divider()

        st.subheader("🌱 꽃잎 변수의 중요도")

        if algorithm in [
            "Random Forest",
            "Decision Tree"
        ]:

            importance_values = model.feature_importances_

            importance_df = pd.DataFrame({

                "변수": FEATURES,

                "중요도": importance_values

            }).sort_values(
                "중요도",
                ascending=True
            )

            fig_importance = go.Figure()

            fig_importance.add_trace(
                go.Bar(
                    x=importance_df["중요도"],
                    y=importance_df["변수"],
                    orientation="h",
                    text=[
                        f"{v * 100:.1f}%"
                        for v in importance_df["중요도"]
                    ],
                    textposition="auto",
                    marker_color="#36A879"
                )
            )

            fig_importance.update_layout(
                xaxis_title="변수 중요도",
                yaxis_title="입력 변수",
                height=300,
                xaxis=dict(range=[0, 1])
            )

            st.plotly_chart(
                fig_importance,
                use_container_width=True
            )

            st.caption(
                "변수 중요도는 모델 전체의 분류에서 "
                "각 변수가 기여한 상대적인 중요도입니다."
            )

        else:

            st.info("""
            KNN은 의사결정나무처럼 변수 중요도를
            직접 계산하는 알고리즘이 아닙니다.

            따라서 변수 중요도 그래프 대신
            가까운 이웃 데이터의 품종을 비교하여
            분류 결과를 이해할 수 있습니다.
            """)


        # ------------------------------------------
        # 상세 모델 평가
        # ------------------------------------------

        with st.expander("📋 모델 평가 상세 정보"):

            st.write(
                f"사용 알고리즘: {algorithm}"
            )

            st.write(
                f"테스트 정확도: {accuracy * 100:.2f}%"
            )

            st.text(report)


# ==================================================
# 12. 하단 안내
# ==================================================

st.divider()

st.caption(
    "🌸 Iris 품종 예측 시스템 | "
    "Pandas + Scikit-learn + Plotly + Streamlit"
)

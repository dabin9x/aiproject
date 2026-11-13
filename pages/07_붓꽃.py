
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


# --------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------

st.set_page_config(
    page_title="붓꽃 품종 예측 시스템",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃(Iris) 품종 예측 시스템")
st.markdown(
    "꽃잎의 길이와 너비를 입력하면 머신러닝이 "
    "붓꽃의 품종을 예측합니다."
)

st.divider()


# --------------------------------------------------
# 2. 데이터 불러오기
# --------------------------------------------------

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
            "Iris.csv 파일을 찾을 수 없습니다. "
            "app.py와 같은 폴더에 Iris.csv를 넣어주세요."
        )

    # 한글 인코딩 처리
    for encoding in ["cp949", "utf-8-sig", "euc-kr", "utf-8"]:
        try:
            data = pd.read_csv(
                file_path,
                encoding=encoding
            )
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("CSV 파일 인코딩을 확인해주세요.")

    required_columns = [
        "꽃잎 길이",
        "꽃잎 너비",
        "품종"
    ]

    for col in required_columns:
        if col not in data.columns:
            raise ValueError(
                f"CSV 파일에 '{col}' 컬럼이 없습니다."
            )

    data = data[required_columns].copy()

    data["꽃잎 길이"] = pd.to_numeric(
        data["꽃잎 길이"], errors="coerce"
    )

    data["꽃잎 너비"] = pd.to_numeric(
        data["꽃잎 너비"], errors="coerce"
    )

    data = data.dropna()

    return data


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


# --------------------------------------------------
# 3. 데이터 분석 및 입력 범위 설정
# --------------------------------------------------

FEATURES = ["꽃잎 길이", "꽃잎 너비"]
TARGET = "품종"

X = df[FEATURES]
y = df[TARGET]

min_length = float(df["꽃잎 길이"].min())
max_length = float(df["꽃잎 길이"].max())

min_width = float(df["꽃잎 너비"].min())
max_width = float(df["꽃잎 너비"].max())


# --------------------------------------------------
# 4. Random Forest 모델 학습
# --------------------------------------------------

@st.cache_resource
def train_model(data):

    X_data = data[FEATURES]
    y_data = data[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X_data,
        y_data,
        test_size=0.2,
        random_state=42,
        stratify=y_data
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        max_depth=5,
        min_samples_split=2,
        class_weight="balanced"
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    return model, accuracy, y_test, predictions


model, accuracy, y_test, predictions = train_model(df)


# --------------------------------------------------
# 5. 데이터 기본 정보
# --------------------------------------------------

st.subheader("📊 데이터 기본 정보")

col1, col2, col3 = st.columns(3)

col1.metric("전체 데이터", f"{len(df)}개")
col2.metric("붓꽃 품종", f"{df[TARGET].nunique()}종")
col3.metric("모델 테스트 정확도", f"{accuracy * 100:.1f}%")


with st.expander("품종별 데이터 개수 확인"):

    st.dataframe(
        df[TARGET].value_counts().rename("데이터 개수"),
        use_container_width=True
    )


st.divider()


# --------------------------------------------------
# 6. 사용자 입력
# --------------------------------------------------

st.subheader("✏️ 꽃잎 크기 입력하기")

st.info(
    f"""
    📌 입력 가능한 범위를 확인하세요.

    - 꽃잎 길이: {min_length} ~ {max_length} cm
    - 꽃잎 너비: {min_width} ~ {max_width} cm

    입력 범위는 Iris.csv에 들어 있는 실제 측정값을 기준으로 합니다.
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


# --------------------------------------------------
# 7. 품종 예측
# --------------------------------------------------

if st.button(
    "🌸 붓꽃 품종 예측하기",
    type="primary",
    use_container_width=True
):

    input_data = pd.DataFrame(
        [[petal_length, petal_width]],
        columns=FEATURES
    )

    predicted_species = model.predict(input_data)[0]

    probabilities = model.predict_proba(input_data)[0]

    probability_df = pd.DataFrame({
        "품종": model.classes_,
        "예측 확률": probabilities * 100
    })

    probability_df = probability_df.sort_values(
        "예측 확률",
        ascending=False
    )

    st.session_state["prediction"] = predicted_species
    st.session_state["probabilities"] = probability_df
    st.session_state["input_length"] = petal_length
    st.session_state["input_width"] = petal_width


# --------------------------------------------------
# 8. 예측 결과 출력
# --------------------------------------------------

if "prediction" in st.session_state:

    predicted_species = st.session_state["prediction"]
    probability_df = st.session_state["probabilities"]

    petal_length = st.session_state["input_length"]
    petal_width = st.session_state["input_width"]

    st.divider()

    st.subheader("🎯 붓꽃 품종 예측 결과")

    st.success(
        f"예측된 붓꽃 품종은 {predicted_species} 입니다! 🌸"
    )

    result_col1, result_col2 = st.columns(2)

    result_col1.metric(
        "꽃잎 길이",
        f"{petal_length:.1f} cm"
    )

    result_col2.metric(
        "꽃잎 너비",
        f"{petal_width:.1f} cm"
    )

    # 품종별 예측 확률
    st.subheader("📈 품종별 예측 확률")

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
                "#2E8B57" if name == predicted_species
                else "#7BA7D7"
                for name in probability_df["품종"]
            ]
        )
    )

    fig_prob.update_layout(
        xaxis_title="예측 확률 (%)",
        yaxis_title="품종",
        xaxis=dict(range=[0, 100]),
        height=300,
        showlegend=False
    )

    st.plotly_chart(
        fig_prob,
        use_container_width=True
    )

    # --------------------------------------------------
    # 9. 분류 영역 시각화
    # --------------------------------------------------

    st.divider()

    st.subheader("🗺️ 품종별 분류 영역 시각화")

    st.markdown(
        """
        그래프의 배경색은 Random Forest가 판단한 품종별 분류 영역입니다.

        - 파란색 계열: Setosa
        - 주황색 계열: Versicolor
        - 보라색 계열: Virginica
        - 🟢 초록색 별: 사용자가 입력한 꽃잎 크기
        """
    )

    # 그래프용 좌표 생성
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

    xx, yy = np.meshgrid(x_range, y_range)

    grid_data = pd.DataFrame({
        "꽃잎 길이": xx.ravel(),
        "꽃잎 너비": yy.ravel()
    })

    # 각 좌표의 품종 예측
    grid_predictions = model.predict(grid_data)

    # 품종을 숫자로 변환
    class_names = list(model.classes_)

    class_mapping = {
        name: index
        for index, name in enumerate(class_names)
    }

    zz = np.array([
        class_mapping[name]
        for name in grid_predictions
    ]).reshape(xx.shape)

    # 그래프 생성
    fig = go.Figure()

    # 배경 분류 영역
    colorscale = [
        [0.0, "#9CC9F0"],
        [0.3332, "#9CC9F0"],
        [0.3333, "#F8C88B"],
        [0.6665, "#F8C88B"],
        [0.6666, "#C5A5E8"],
        [1.0, "#C5A5E8"]
    ]

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

    # 기존 데이터 품종별 표시
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
                ),
                hovertemplate=(
                    "품종: " + species +
                    "<br>꽃잎 길이: %{x:.1f} cm" +
                    "<br>꽃잎 너비: %{y:.1f} cm"
                    "<extra></extra>"
                )
            )
        )

    # 사용자 입력값: 초록색 별
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
            ),
            hovertemplate=(
                "사용자 입력값"
                "<br>꽃잎 길이: %{x:.1f} cm"
                "<br>꽃잎 너비: %{y:.1f} cm"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title="Random Forest 품종 분류 영역",
        xaxis_title="꽃잎 길이 (cm)",
        yaxis_title="꽃잎 너비 (cm)",
        height=650,
        template="plotly_white",
        legend_title="범례",
        hovermode="closest"
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

    # --------------------------------------------------
    # 10. 왜 해당 품종으로 분류되었을까?
    # --------------------------------------------------

    st.divider()

    st.subheader("🔍 왜 이 품종으로 분류되었을까요?")

    st.markdown(
        f"""
        입력한 값은 다음과 같습니다.

        - 꽃잎 길이: **{petal_length:.1f} cm**
        - 꽃잎 너비: **{petal_width:.1f} cm**

        Random Forest 모델은 입력값이 위치한
        분류 영역과 여러 의사결정나무의 예측을 종합하여
        **{predicted_species}** 품종으로 분류했습니다.
        """
    )

    st.markdown("### 품종별 예측 확률 비교")

    for _, row in probability_df.iterrows():

        species = row["품종"]
        probability = row["예측 확률"]

        st.write(
            f"**{species}** : {probability:.1f}%"
        )

        st.progress(
            float(probability / 100)
        )

    # 변수 중요도
    st.markdown("### 🌱 품종 분류에 사용된 변수의 중요도")

    importance_df = pd.DataFrame({
        "변수": FEATURES,
        "중요도": model.feature_importances_
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
        "변수 중요도는 모델 전체에서 각 변수가 분류에 기여한 "
        "상대적 중요도를 나타냅니다. 개별 예측의 원인이나 "
        "인과관계를 직접 증명하는 값은 아닙니다."
    )

    # --------------------------------------------------
    # 11. 모델 평가
    # --------------------------------------------------

    with st.expander("📋 머신러닝 모델 평가 결과"):

        st.write(
            f"테스트 데이터 정확도: {accuracy * 100:.2f}%"
        )

        st.text(
            classification_report(
                y_test,
                predictions,
                zero_division=0
            )
        )

        st.write("학습에 사용된 알고리즘: Random Forest")

        st.write("의사결정나무 개수: 200개")


# --------------------------------------------------
# 12. 하단 안내
# --------------------------------------------------

st.divider()

st.caption(
    "🌸 Iris 품종 예측 프로젝트 | "
    "Pandas + Scikit-learn + Streamlit + Plotly"
)

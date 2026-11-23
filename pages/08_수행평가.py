    line_x = list(range(int(selected["월순번"].min()), int(next_x) + 1))
    line_dates = [
        pd.Timestamp(year=(v - 1) // 12, month=((v - 1) % 12) + 1, day=1)
        for v in line_x
    ]
    line_y = model.predict(pd.DataFrame({"월순번": line_x}))

    fig.add_trace(go.Scatter(
        x=line_dates,
        y=line_y,
        mode="lines",
        name="선형회귀 추세선",
        line=dict(width=2, dash="dash"),
        hovertemplate="%{x|%Y년 %m월}<br>회귀선 값: %{y:.2f}%<extra></extra>"
    ))

    # 각 실제 관측값과 회귀선 값 사이의 차이(잔차)를 세로선으로 표현합니다.
    fitted = model.predict(X)
    residual_x, residual_y = [], []
    for date, actual, fit_value in zip(selected["날짜"], y, fitted):
        residual_x.extend([date, date, None])
        residual_y.extend([actual, fit_value, None])

    fig.add_trace(go.Scatter(
        x=residual_x,
        y=residual_y,
        mode="lines",
        name="실제값과 회귀선의 차이",
        line=dict(width=1, dash="dot"),
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=[next_date],
        y=[prediction],
        mode="markers",
        name="다음 달 예측값",
        marker=dict(size=16, symbol="star"),
        hovertemplate="%{x|%Y년 %m월}<br>예측 전환율: %{y:.2f}%<extra></extra>"
    ))

    slope = float(model.coef_[0])
    intercept = float(model.intercept_)
    equation_text = f"전환율 = {slope:.4f} × 월순번 + ({intercept:.4f})"

fig.update_layout(
    xaxis_title="월",
    yaxis_title="아파트 전월세 전환율(%)",
    hovermode="x unified",
    legend_title="그래프 항목",
    template="plotly_white",
    height=520,
    margin=dict(l=20, r=20, t=30, b=20)
)
fig.update_yaxes(ticksuffix="%")
fig.update_xaxes(tickformat="%Y년 %m월")

st.plotly_chart(fig, use_container_width=True)

# 핵심 수치
metric1, metric2, metric3 = st.columns(3)
metric1.metric("선택 연도 관측 건수", f"{len(selected)}개월")
metric2.metric("가장 최근 실제 전환율", f"{selected.iloc[-1]['전환율']:.2f}%")
if prediction is not None:
    metric3.metric(
        f"{next_date.year}년 {next_date.month}월 예측 전환율",
        f"{prediction:.2f}%",
        delta=f"{prediction - selected.iloc[-1]['전환율']:+.2f}%p"
    )
else:
    metric3.metric("예측 전환율", "예측 불가")

if prediction is None:
    st.warning(
        "선택한 연도에는 유효한 월별 데이터가 2개 미만입니다. "
        "선형회귀 직선을 학습하려면 최소 2개 이상의 월별 데이터가 필요합니다."
    )
else:
    st.success(
        f"선형회귀 예측 결과: **{next_date.year}년 {next_date.month}월 "
        f"{prediction:.2f}%**"
    )
    st.caption(f"회귀식: `{equation_text}`")

# 원본 데이터 표
with st.expander("📋 선택한 지역의 월별 데이터 표 보기"):
    display_df = selected[["날짜", "전환율"]].copy()
    display_df["날짜"] = display_df["날짜"].dt.strftime("%Y년 %m월")
    display_df = display_df.rename(columns={
        "날짜": "월",
        "전환율": "전월세 전환율(%)"
    })
    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.divider()
st.subheader("💡 선형회귀 알고리즘은 어떻게 예측할까요?")

st.markdown(
    """
    **선형회귀(Linear Regression)**는 과거 데이터의 변화 흐름을 가장 잘 나타내는
    직선을 찾고, 그 직선을 이용해 아직 관측하지 않은 값을 예측하는 방법입니다.

    1. **데이터 입력:** 선택한 지역·연도의 월별 전월세 전환율을 모읍니다.
    2. **직선 찾기:** 월이 지날수록 전환율이 어떻게 변하는지 나타내는 직선을 계산합니다.
    3. **오차 줄이기:** 실제 데이터 점과 직선 사이의 세로 거리(잔차)를 살펴보고,
       잔차 제곱의 합이 가장 작아지도록 직선을 정합니다.
    4. **미래 예측:** 찾은 직선을 다음 달까지 연장해 다음 달 전월세 전환율을 계산합니다.

    **그래프 읽는 방법**
    - 실선과 원형 점: 실제 월별 전월세 전환율
    - 점선: 과거 데이터의 전체적인 흐름을 나타내는 선형회귀 추세선
    - 세로 점선: 실제값과 추세선 사이의 차이(잔차)
    - 별 모양 점: 다음 달 예측 전환율

    **주의:** 예측값은 과거 데이터의 직선적인 추세가 이어진다고 가정한 추정치입니다.
    금리, 주택 시장 상황, 정책 등 미래의 변화를 반영하지 않으므로 실제 결과와 다를 수 있습니다.
    """
)

st.caption(
    f"사용 데이터 파일: {csv_path.name} · "
    "자료에 포함된 월별 전환율을 사용하며, 결측값은 분석에서 제외합니다."
)

    hovertemplate=(
        "<b>남성</b><br>"
        "%{x}<br>"
        "인구: %{y:,.0f}명"
        "<extra></extra>"
    )
))

# 여성: 초록색
fig.add_trace(go.Scatter(
    x=chart_df["연령대"],
    y=chart_df["여성"],
    mode="lines+markers",
    name="여성",
    line=dict(color="#159947", width=3),
    marker=dict(size=8, color="#159947"),
    connectgaps=False,
    hovertemplate=(
        "<b>여성</b><br>"
        "%{x}<br>"
        "인구: %{y:,.0f}명"
        "<extra></extra>"
    )
))

valid_values = [
    value
    for value in male_values + female_values
    if value is not None
]

max_population = max(valid_values, default=100_000)
y_max = max(
    100_000,
    ((max_population // 100_000) + 1) * 100_000
)

fig.update_layout(
    height=600,
    template="plotly_white",
    font=dict(
        family='"Noto Sans KR", "Malgun Gothic", "Apple SD Gothic Neo", sans-serif',
        size=13,
        color="#333333"
    ),
    title=dict(
        text=f"{selected_area} {selected_year}년 연령대별 남녀 인구",
        x=0.02,
        xanchor="left"
    ),
    xaxis=dict(
        title="연령대",
        categoryorder="array",
        categoryarray=ages
    ),
    yaxis=dict(
        title="인구수 (명)",
        range=[0, y_max],
        tick0=0,
        dtick=100_000,
        tickformat=",",
        gridcolor="#E8E8E8",
        griddash="dash"
    ),
    legend=dict(
        title="성별",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    hovermode="x unified",
    margin=dict(l=30, r=30, t=90, b=50)
)

st.plotly_chart(fig, use_container_width=True)

st.caption(
    "※ 핑크색 선은 남성, 초록색 선은 여성입니다. "
    "세로축 가로 눈금선은 10만 명 단위입니다. "
    "그래프에 마우스를 올리면 연령대별 인구수를 확인할 수 있습니다."
)

# ------------------------------------------------------------
# 7. 연령대별 데이터 표
# ------------------------------------------------------------

with st.expander("📋 연령대별 남녀 인구 데이터 표 보기"):
    display_df = chart_df.copy()

    for column in ["남성", "여성"]:
        display_df[column] = display_df[column].apply(
            lambda value: f"{value:,}명" if pd.notna(value) else "-"
        )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

# ------------------------------------------------------------
# 8. 데이터 정보
# ------------------------------------------------------------

with st.expander("ℹ️ 데이터 및 인코딩 정보"):
    missing_count = int(df.isna().sum().sum())

    st.write(f"CSV 파일 위치: `{DATA_FILE}`")
    st.write(f"사용한 CSV 인코딩: **{used_encoding}**")
    st.write(f"데이터 크기: **{df.shape[0]}행 × {df.shape[1] - 1}열**")
    st.write(f"결측치 개수: **{missing_count:,}개**")
    st.write("그래프 라이브러리: **Plotly**")

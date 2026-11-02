second_rate = chart_df.iloc[1]["비율"]


# ---------------------------------------------------------
# 핵심 지표
# ---------------------------------------------------------
st.subheader(f"📊 {selected_country} MBTI 분포")

metric1, metric2, metric3 = st.columns(3)
metric1.metric("가장 높은 유형", top_type)
metric2.metric("1위 비율", f"{top_rate:.2f}%")
metric3.metric("2위 유형", f"{second_type} · {second_rate:.2f}%")


# ---------------------------------------------------------
# 막대그래프 색상
# 1위: 빨간색
# 2위~16위: 진한 파랑에서 연한 파랑으로
# ---------------------------------------------------------
blue_gradient = [
    "#1769AA",
    "#287FC0",
    "#3D94D2",
    "#55A7DF",
    "#70B8E8",
    "#8BC7EF",
    "#A5D4F3",
    "#B9DFF6",
    "#C8E6F8",
    "#D2EBFA",
    "#DAEFFB",
    "#E1F2FC",
    "#E7F5FD",
    "#ECF7FD",
    "#F1F9FE",
]

bar_colors = ["#E53935"] + blue_gradient[: len(chart_df) - 1]

fig = go.Figure(
    data=[
        go.Bar(
            x=chart_df["MBTI"],
            y=chart_df["비율"],
            marker=dict(
                color=bar_colors,
                line=dict(color="rgba(0,0,0,0)", width=0),
            ),
            text=[f"{value:.2f}%" for value in chart_df["비율"]],
            textposition="outside",
            textfont=dict(size=12),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "비율: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    ]
)

fig.update_layout(
    title=dict(
        text=f"{selected_country}의 MBTI 유형별 비율",
        x=0.02,
        xanchor="left",
    ),
    xaxis_title="MBTI 유형",
    yaxis_title="비율 (%)",
    yaxis=dict(
        rangemode="tozero",
        ticksuffix="%",
        gridcolor="rgba(128,128,128,0.18)",
    ),
    xaxis=dict(categoryorder="array", categoryarray=chart_df["MBTI"].tolist()),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=70, b=20),
    height=540,
    showlegend=False,
)

st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------
# 유형별 순위표
# ---------------------------------------------------------
with st.expander("📋 MBTI 유형별 상세 순위 보기", expanded=True):
    display_df = chart_df.copy()
    display_df.insert(0, "순위", range(1, len(display_df) + 1))
    display_df["비율"] = display_df["비율"].map(lambda x: f"{x:.2f}%")
    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
    )


# ---------------------------------------------------------
# 데이터 참고 안내
# ---------------------------------------------------------
with st.expander("ℹ️ 데이터 해석 시 참고사항"):
    st.write(
        """
        - 그래프의 빨간색 막대는 선택 국가에서 비율이 가장 높은 MBTI 유형입니다.
        - 나머지 유형은 높은 순서부터 진한 파란색에서 연한 파란색으로 표시됩니다.
        - 원본 데이터가 0~1 사이의 소수 비율이면 자동으로 100을 곱해 백분율로 표시합니다.
        - 국가별 비율의 합계가 정확히 100%가 아닐 수 있습니다.
        - 조사 시기, 표본 크기, 조사 방법이 확인되지 않은 경우 결과는 참고용 통계로 해석해야 합니다.
        """
    )

st.caption("Data source: countriesMBTI_16types.csv")

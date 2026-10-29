import streamlit as st

# ==========================================
# 🌟 MBTI 진로 탐험소
# Streamlit 기본 기능만 사용
# ==========================================

st.set_page_config(
    page_title="MBTI 진로 탐험소 🌈",
    page_icon="🌈",
    layout="wide"
)

# 🎨 디자인
st.markdown("""
<style>
    .stApp {
        background-color: #F7F8FF;
    }

    .main-title {
        text-align: center;
        color: #5546A8;
        font-size: 40px;
        font-weight: bold;
        margin-bottom: 10px;
    }

    .sub-title {
        text-align: center;
        color: #62677A;
        font-size: 17px;
        margin-bottom: 25px;
    }

    .career-card {
        background-color: white;
        padding: 24px;
        border-radius: 18px;
        border: 1px solid #E3E4F5;
        margin-bottom: 15px;
    }

    .career-name {
        color: #5546A8;
        font-size: 24px;
        font-weight: bold;
    }

    .career-info {
        color: #353849;
        font-size: 16px;
        line-height: 1.8;
    }

    .salary {
        background-color: #EEEAFE;
        padding: 12px;
        border-radius: 10px;
        color: #5546A8;
        font-weight: bold;
        margin-top: 12px;
    }

    .notice {
        background-color: #FFF4D9;
        padding: 16px;
        border-radius: 12px;
        color: #66501B;
        line-height: 1.7;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 💼 직업 정보 데이터
# 연봉은 국내 기준의 대략적인 참고 추정치
# ==========================================

jobs = {
    "developer": {
        "name": "💻 소프트웨어 개발자",
        "desc": "웹사이트, 앱, 프로그램을 만드는 직업이야.",
        "major": "컴퓨터공학과, 소프트웨어학과, 인공지능학과",
        "personality": "논리적으로 생각하고, 문제를 해결하며, 새로운 기술을 배우는 걸 좋아하는 사람",
        "salary": "약 3,500만~7,000만 원"
    },
    "data": {
        "name": "📊 데이터 분석가",
        "desc": "다양한 데이터를 분석해서 중요한 정보와 해결책을 찾아내.",
        "major": "통계학과, 데이터사이언스학과, 산업공학과",
        "personality": "숫자와 자료를 꼼꼼히 살펴보고, 근거를 바탕으로 판단하는 사람",
        "salary": "약 3,500만~7,000만 원"
    },
    "designer": {
        "name": "🎨 UX/UI 디자이너",
        "desc": "사람들이 웹사이트와 앱을 편리하게 사용할 수 있도록 디자인해.",
        "major": "시각디자인학과, 산업디자인학과, 디지털미디어학과",
        "personality": "창의적이고 관찰력이 좋으며, 다른 사람의 입장을 생각하는 사람",
        "salary": "약 3,000만~6,000만 원"
    },
    "writer": {
        "name": "✍️ 작가·콘텐츠 기획자",
        "desc": "글과 이야기, 콘텐츠를 기획하고 사람들에게 새로운 생각을 전달해.",
        "major": "국어국문학과, 문예창작학과, 미디어커뮤니케이션학과",
        "personality": "상상력이 풍부하고 표현하는 것을 좋아하며, 꾸준히 글을 쓸 수 있는 사람",
        "salary": "약 2,800만~5,500만 원"
    },
    "teacher": {
        "name": "📚 교사",
        "desc": "학생들이 지식을 배우고 자신의 가능성을 발견하도록 도와줘.",
        "major": "교육학과, 사범대학 관련 학과, 초등교육과",
        "personality": "책임감이 있고 설명하는 것을 좋아하며, 다른 사람의 성장을 돕는 사람",
        "salary": "약 3,500만~7,000만 원"
    },
    "counselor": {
        "name": "💗 상담 전문가",
        "desc": "사람들의 고민을 듣고 스스로 해결책을 찾아가도록 도와줘.",
        "major": "심리학과, 상담심리학과, 교육학과",
        "personality": "공감 능력이 있고, 잘 들어주며, 상대방을 존중하는 사람",
        "salary": "약 3,000만~5,500만 원"
    },
    "doctor": {
        "name": "🩺 의사",
        "desc": "질병을 진단하고 치료하며 사람들의 건강을 지켜.",
        "major": "의예과·의학과",
        "personality": "책임감이 강하고, 과학에 관심이 있으며, 꾸준히 공부할 수 있는 사람",
        "salary": "약 1억~2억 원 이상"
    },
    "nurse": {
        "name": "🏥 간호사",
        "desc": "환자를 돌보고 의료진과 협력해 건강 회복을 도와줘.",
        "major": "간호학과",
        "personality": "세심하고 책임감이 있으며, 협력과 소통을 중요하게 생각하는 사람",
        "salary": "약 3,500만~6,000만 원"
    },
    "researcher": {
        "name": "🔬 과학 연구원",
        "desc": "실험과 연구를 통해 새로운 지식과 기술을 발견해.",
        "major": "생명과학과, 화학과, 물리학과 등 관심 분야의 학과",
        "personality": "호기심이 많고, 관찰을 즐기며, 한 가지 문제를 깊이 탐구하는 사람",
        "salary": "약 3,500만~7,000만 원"
    },
    "engineer": {
        "name": "⚙️ 기계·전기 엔지니어",
        "desc": "기계와 전기 시스템을 설계하고 개선하는 일을 해.",
        "major": "기계공학과, 전기전자공학과, 메카트로닉스공학과",
        "personality": "논리적이고 꼼꼼하며, 실제 문제를 해결하는 데 흥미가 있는 사람",
        "salary": "약 3,500만~7,000만 원"
    },
    "lawyer": {
        "name": "⚖️ 변호사",
        "desc": "법률 지식을 바탕으로 사람과 조직의 권리를 보호해.",
        "major": "법학과 등 다양한 학부 전공 후 법학전문대학원 진학",
        "personality": "논리적이고 분석력이 좋으며, 자신의 생각을 명확하게 전달하는 사람",
        "salary": "약 5,000만~1억 5,000만 원 이상"
    },
    "marketer": {
        "name": "📣 마케팅 전문가",
        "desc": "사람들의 관심과 시장 흐름을 분석해 제품과 서비스를 알리는 일을 해.",
        "major": "경영학과, 광고홍보학과, 미디어커뮤니케이션학과",
        "personality": "아이디어가 많고, 사람들의 관심사를 잘 파악하며, 소통을 즐기는 사람",
        "salary": "약 3,000만~6,500만 원"
    },
    "entrepreneur": {
        "name": "🚀 창업가",
        "desc": "새로운 아이디어를 사업으로 발전시키고 팀과 함께 성장시켜.",
        "major": "경영학과, 경제학과, 창업 관련 학과 등",
        "personality": "도전 정신이 있고, 문제 해결을 즐기며, 변화에 유연한 사람",
        "salary": "개인차가 매우 큼"
    },
    "accountant": {
        "name": "🧮 회계·재무 전문가",
        "desc": "기업의 돈의 흐름을 분석하고 재무 상태를 관리해.",
        "major": "회계학과, 경영학과, 경제학과",
        "personality": "꼼꼼하고 정직하며, 숫자를 다루고 규칙을 지키는 것을 좋아하는 사람",
        "salary": "약 3,500만~7,000만 원"
    },
    "architect": {
        "name": "🏙️ 건축가",
        "desc": "사람들이 생활하고 활동할 공간을 계획하고 설계해.",
        "major": "건축학과, 건축공학과",
        "personality": "공간 감각이 좋고, 창의적이며, 현실적인 조건도 함께 고려하는 사람",
        "salary": "약 3,000만~6,000만 원"
    },
    "environment": {
        "name": "🌱 환경 연구원",
        "desc": "환경 문제를 조사하고 자연과 인간이 공존할 방법을 연구해.",
        "major": "환경공학과, 환경과학과, 생명과학과",
        "personality": "자연에 관심이 많고, 탐구심과 책임감을 가진 사람",
        "salary": "약 3,300만~6,500만 원"
    },
    "journalist": {
        "name": "📰 기자",
        "desc": "사건과 사회 문제를 취재하고 정확한 정보를 전달해.",
        "major": "신문방송학과, 미디어커뮤니케이션학과, 정치외교학과 등",
        "personality": "호기심이 많고, 질문을 잘하며, 사실을 꼼꼼하게 확인하는 사람",
        "salary": "약 3,000만~6,500만 원"
    },
    "film": {
        "name": "🎬 영상 제작자",
        "desc": "영상의 기획부터 촬영과 편집까지 콘텐츠를 만들어.",
        "major": "영상학과, 영화학과, 방송영상학과",
        "personality": "창의적이고, 이야기를 시각적으로 표현하는 것을 좋아하는 사람",
        "salary": "약 2,800만~6,000만 원"
    },
    "hr": {
        "name": "🤝 인사·조직문화 전문가",
        "desc": "직원을 채용하고 조직이 원활하게 일할 수 있도록 지원해.",
        "major": "경영학과, 심리학과, 행정학과",
        "personality": "사람에 대한 관심이 많고, 공정하며, 의견을 조율하는 데 능숙한 사람",
        "salary": "약 3,500만~7,000만 원"
    },
    "diplomat": {
        "name": "🌍 외교관·국제협력 전문가",
        "desc": "국가와 국제기구 사이에서 소통하고 국제 문제 해결에 참여해.",
        "major": "정치외교학과, 국제학과, 경제학과, 어문계열 학과 등",
        "personality": "다양한 문화를 존중하고, 소통 능력과 분석력을 갖춘 사람",
        "salary": "약 4,000만~8,000만 원"
    },
    "financial": {
        "name": "💹 금융 분석가",
        "desc": "경제와 금융 자료를 분석해 기업과 고객의 의사결정을 도와.",
        "major": "경제학과, 금융학과, 경영학과, 통계학과",
        "personality": "분석적이고 꼼꼼하며, 경제 흐름에 관심이 많은 사람",
        "salary": "약 4,000만~8,000만 원"
    },
    "product": {
        "name": "🧩 서비스·제품 기획자",
        "desc": "사용자의 요구를 파악하고 더 좋은 서비스나 제품을 기획해.",
        "major": "산업공학과, 경영학과, 컴퓨터공학과, 디자인 관련 학과",
        "personality": "문제의 핵심을 파악하고, 다양한 의견을 정리하며, 실행 계획을 세우는 사람",
        "salary": "약 3,500만~7,000만 원"
    },
    "game": {
        "name": "🎮 게임 기획자",
        "desc": "게임의 규칙과 이야기, 콘텐츠를 설계하고 개발팀과 협력해.",
        "major": "게임학과, 컴퓨터공학과, 디지털콘텐츠학과",
        "personality": "상상력이 풍부하고, 게임을 분석하며, 팀과 협력하는 것을 좋아하는 사람",
        "salary": "약 3,000만~6,000만 원"
    },
    "artist": {
        "name": "🖌️ 일러스트레이터",
        "desc": "그림과 시각적 표현으로 책, 광고, 게임 등의 콘텐츠를 만들어.",
        "major": "회화과, 시각디자인학과, 애니메이션학과",
        "personality": "표현력이 좋고, 관찰력이 뛰어나며, 꾸준히 작품을 발전시키는 사람",
        "salary": "약 2,500만~5,000만 원"
    },
    "social": {
        "name": "💞 사회복지사",
        "desc": "도움이 필요한 사람들이 필요한 서비스를 이용하고 생활을 개선하도록 지원해.",
        "major": "사회복지학과, 사회학과, 아동·가족 관련 학과",
        "personality": "공감 능력이 있고, 책임감이 강하며, 사람을 존중하는 사람",
        "salary": "약 2,800만~4,500만 원"
    },
    "chef": {
        "name": "🍳 요리사·셰프",
        "desc": "음식을 개발하고 조리하며 새로운 맛과 메뉴를 만들어.",
        "major": "조리학과, 외식경영학과, 식품영양학과",
        "personality": "손재주가 좋고, 창의적이며, 반복적인 연습을 꾸준히 하는 사람",
        "salary": "약 2,800만~5,000만 원"
    },
    "vet": {
        "name": "🐾 수의사",
        "desc": "동물을 진료하고 질병을 예방하며 동물의 건강을 지켜.",
        "major": "수의예과·수의학과",
        "personality": "동물을 아끼고, 관찰력이 좋으며, 책임감 있게 판단하는 사람",
        "salary": "약 5,000만~9,000만 원"
    },
    "marketing_data": {
        "name": "📈 마케팅 데이터 분석가",
        "desc": "소비자와 시장 데이터를 분석해 마케팅 전략을 개선해.",
        "major": "통계학과, 경영학과, 데이터사이언스학과",
        "personality": "숫자를 분석하는 능력과 창의적인 문제 해결력을 함께 가진 사람",
        "salary": "약 3,500만~7,000만 원"
    },
    "public": {
        "name": "🏛️ 공공정책 연구원",
        "desc": "사회 문제와 정책을 분석해 더 나은 제도와 해결책을 제안해.",
        "major": "행정학과, 정치외교학과, 경제학과, 사회학과",
        "personality": "사회 문제에 관심이 많고, 자료를 분석하며, 공익을 중요하게 생각하는 사람",
        "salary": "약 3,500만~7,000만 원"
    },
    "education": {
        "name": "🧑‍🏫 교육 콘텐츠 개발자",
        "desc": "학생들이 재미있고 효과적으로 배울 수 있는 교육 자료와 콘텐츠를 만들어.",
        "major": "교육학과, 교육공학과, 국어교육과, 컴퓨터교육과 등",
        "personality": "설명하는 것을 좋아하고, 학습자의 입장에서 생각하며, 창의적인 사람",
        "salary": "약 3,000만~6,000만 원"
    },
    "security": {
        "name": "🔐 정보보안 전문가",
        "desc": "컴퓨터 시스템과 정보를 사이버 공격으로부터 안전하게 지켜.",
        "major": "정보보호학과, 컴퓨터공학과, 소프트웨어학과",
        "personality": "꼼꼼하고 논리적이며, 문제를 추적하고 해결하는 것을 좋아하는 사람",
        "salary": "약 3,500만~8,000만 원"
    },
    "sales": {
        "name": "💬 영업·고객 컨설턴트",
        "desc": "고객의 필요를 파악하고 적합한 제품이나 서비스를 제안해.",
        "major": "경영학과, 경제학과, 마케팅 관련 학과 등",
        "personality": "소통을 즐기고, 상대방의 요구를 파악하며, 목표를 세우는 사람",
        "salary": "약 3,000만~7,000만 원"
    }
}


# ==========================================
# 🌈 MBTI별 추천 진로
# ==========================================

mbti_data = {
    "ISTJ": {
        "emoji": "📋",
        "title": "청렴결백한 현실주의자",
        "intro": "계획적이고 꼼꼼한 편이라 체계적으로 일하는 분야를 탐색해 보면 좋아!",
        "jobs": ["accountant", "engineer"]
    },
    "ISFJ": {
        "emoji": "🌷",
        "title": "용감한 수호자",
        "intro": "책임감과 배려심을 살릴 수 있는 진로를 찾아보자!",
        "jobs": ["nurse", "teacher"]
    },
    "INFJ": {
        "emoji": "🌌",
        "title": "선의의 옹호자",
        "intro": "사람과 사회를 이해하고 더 나은 변화를 만드는 분야를 살펴봐!",
        "jobs": ["counselor", "writer"]
    },
    "INTJ": {
        "emoji": "♟️",
        "title": "용의주도한 전략가",
        "intro": "큰 그림을 그리고 복잡한 문제를 해결하는 분야에 도전해 봐!",
        "jobs": ["developer", "researcher"]
    },
    "ISTP": {
        "emoji": "🛠️",
        "title": "만능 재주꾼",
        "intro": "직접 분석하고 실험하면서 해결책을 찾는 분야가 잘 맞을 수 있어!",
        "jobs": ["engineer", "security"]
    },
    "ISFP": {
        "emoji": "🎨",
        "title": "호기심 많은 예술가",
        "intro": "자신만의 감각과 표현력을 활용할 수 있는 분야를 알아보자!",
        "jobs": ["designer", "artist"]
    },
    "INFP": {
        "emoji": "🦋",
        "title": "열정적인 중재자",
        "intro": "가치관과 상상력을 살리고 사람들에게 의미를 전하는 일을 탐색해 봐!",
        "jobs": ["writer", "social"]
    },
    "INTP": {
        "emoji": "🧪",
        "title": "논리적인 사색가",
        "intro": "궁금한 것을 깊이 파고들고 새로운 원리를 발견하는 분야를 추천해!",
        "jobs": ["data", "researcher"]
    },
    "ESTP": {
        "emoji": "⚡",
        "title": "모험을 즐기는 사업가",
        "intro": "빠르게 상황을 파악하고 사람들과 소통하는 분야를 살펴보자!",
        "jobs": ["sales", "entrepreneur"]
    },
    "ESFP": {
        "emoji": "🎉",
        "title": "자유로운 연예인",
        "intro": "활기찬 에너지와 표현력을 활용하는 진로를 알아보면 좋겠어!",
        "jobs": ["film", "marketer"]
    },
    "ENFP": {
        "emoji": "🌈",
        "title": "재기발랄한 활동가",
        "intro": "새로운 아이디어를 만들고 다양한 사람들과 협력하는 분야를 탐색해 봐!",
        "jobs": ["marketer", "game"]
    },
    "ENTP": {
        "emoji": "💡",
        "title": "뜨거운 논쟁을 즐기는 변론가",
        "intro": "새로운 가능성을 발견하고 아이디어를 발전시키는 일을 추천해!",
        "jobs": ["entrepreneur", "product"]
    },
    "ESTJ": {
        "emoji": "📊",
        "title": "엄격한 관리자",
        "intro": "목표를 세우고 조직과 일을 체계적으로 이끄는 분야를 살펴보자!",
        "jobs": ["hr", "accountant"]
    },
    "ESFJ": {
        "emoji": "🤝",
        "title": "사교적인 외교관",
        "intro": "사람들과 협력하고 공동체에 기여하는 진로를 찾아보자!",
        "jobs": ["teacher", "hr"]
    },
    "ENFJ": {
        "emoji": "🌟",
        "title": "정의로운 사회운동가",
        "intro": "사람들의 성장을 돕고 팀을 이끄는 분야에서 강점을 발휘할 수 있어!",
        "jobs": ["education", "counselor"]
    },
    "ENTJ": {
        "emoji": "🚀",
        "title": "대담한 통솔자",
        "intro": "전략적으로 목표를 세우고 여러 사람과 프로젝트를 이끄는 분야를 알아보자!",
        "jobs": ["product", "financial"]
    }
}


# ==========================================
# 🖥️ 화면 구성
# ==========================================

st.markdown(
    '<div class="main-title">🌈 MBTI 진로 탐험소</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '나의 성향을 알아보고 미래의 직업을 탐험해 보자! 🚀'
    '</div>',
    unsafe_allow_html=True
)

st.info(
    "💡 MBTI는 진로를 확정하는 검사가 아니야. "
    "내 흥미와 능력도 함께 살펴보면서 다양한 가능성을 탐색해 봐!"
)

st.divider()

st.subheader("🔎 나의 MBTI를 선택해 줘!")

mbti_options = list(mbti_data.keys())

selected_mbti = st.selectbox(
    "16가지 유형 중 하나를 선택해 봐!",
    mbti_options,
    format_func=lambda x: (
        f"{x}  {mbti_data[x]['emoji']}  "
        f"- {mbti_data[x]['title']}"
    )
)

if st.button("✨ 내 진로 알아보기", use_container_width=True):

    st.session_state["selected_mbti"] = selected_mbti

if "selected_mbti" in st.session_state:

    result_mbti = st.session_state["selected_mbti"]
    result = mbti_data[result_mbti]

    st.divider()

    st.markdown(
        f"## {result['emoji']} {result_mbti} 유형의 진로 탐험"
    )

    st.subheader(result["title"])
    st.write(result["intro"])

    st.success(
        "🎯 아래 직업들은 이 유형의 성향을 바탕으로 골라 본 "
        "진로 아이디어야. 실제 적합성은 사람마다 다를 수 있어!"
    )

    col1, col2 = st.columns(2)

    for index, job_id in enumerate(result["jobs"]):

        job = jobs[job_id]
        current_col = col1 if index == 0 else col2

        with current_col:

            st.markdown(
                f"""
                <div class="career-card">
                    <div class="career-name">
                        {job['name']}
                    </div>
                    <p class="career-info">
                        {job['desc']}
                    </p>
                    <hr>
                    <p class="career-info">
                        🎓 <b>관련 학과</b><br>
                        {job['major']}
                    </p>
                    <p class="career-info">
                        🧠 <b>도움이 되는 성격·역량</b><br>
                        {job['personality']}
                    </p>
                    <div class="salary">
                        💰 참고 연봉: {job['salary']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()

    st.subheader("🌱 나만의 진로 탐색 미션")

    st.write("추천 직업 중 하나를 골라 아래 미션을 해 보자!")

    mission = st.radio(
        "어떤 활동부터 해 볼까?",
        [
            "🎥 관련 직업을 소개하는 영상 찾아보기",
            "📚 관심 있는 학과의 교육과정 알아보기",
            "📝 그 직업에 필요한 능력 3가지 적어보기",
            "🧩 관련된 작은 프로젝트 직접 해보기"
        ],
        key="career_mission"
    )

    st.write(f"💪 오늘의 미션: **{mission}**")

    st.markdown(
        """
        <div class="notice">
            💰 <b>연봉 정보 안내</b><br>
            화면에 표시된 금액은 직업 탐색을 위한 대략적인 참고 추정치야.
            모든 직업에 대해 동일한 조사 기준으로 확인한 공식 평균값은 아니야.
            실제 연봉은 경력, 회사 규모, 지역, 자격 및 전문성에 따라 달라질 수 있어.
            정확한 직업별 임금은 한국고용정보원의 직업정보를 확인해 봐!
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "🌟 MBTI는 가능성을 탐색하는 출발점일 뿐이야. "
        "네가 좋아하는 활동과 직접 경험해 본 결과도 중요해!"
    )

else:

    st.markdown(
        """
        <div class="career-card">
            <h3>🗺️ 진로 탐험은 이렇게 진행돼!</h3>
            <p>1️⃣ 나의 MBTI 유형을 선택해.</p>
            <p>2️⃣ 추천 직업 두 가지를 확인해.</p>
            <p>3️⃣ 관련 학과와 필요한 역량을 살펴봐.</p>
            <p>4️⃣ 관심 있는 진로를 직접 탐색해 봐!</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

st.markdown(
    "<div style='text-align:center; color:#777;'>"
    "🌈 나의 가능성은 MBTI보다 훨씬 넓어! 🌈"
    "</div>",
    unsafe_allow_html=True
)

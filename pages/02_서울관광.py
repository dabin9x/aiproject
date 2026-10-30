```python
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Seoul Top 10 Attractions",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Seoul Top 10 Tourist Attractions")
st.write("Explore Seoul's popular tourist attractions on an interactive map.")

# 관광지 데이터: CSV 파일 불필요
attractions = [
    {
        "rank": 1,
        "name": "Gyeongbokgung Palace",
        "korean": "경복궁",
        "lat": 37.5796,
        "lon": 126.9770,
        "category": "Palace",
        "description": "A famous royal palace from the Joseon dynasty."
    },
    {
        "rank": 2,
        "name": "N Seoul Tower",
        "korean": "N서울타워",
        "lat": 37.5512,
        "lon": 126.9882,
        "category": "Viewpoint",
        "description": "Enjoy panoramic views of Seoul from Namsan Mountain."
    },
    {
        "rank": 3,
        "name": "Bukchon Hanok Village",
        "korean": "북촌한옥마을",
        "lat": 37.5826,
        "lon": 126.9830,
        "category": "Traditional Culture",
        "description": "Explore traditional Korean houses and historic alleys."
    },
    {
        "rank": 4,
        "name": "Myeongdong",
        "korean": "명동",
        "lat": 37.5636,
        "lon": 126.9869,
        "category": "Shopping",
        "description": "A popular shopping district with fashion and street food."
    },
    {
        "rank": 5,
        "name": "Namsan Park",
        "korean": "남산공원",
        "lat": 37.5503,
        "lon": 126.9900,
        "category": "Park",
        "description": "A green urban park with walking paths and city views."
    },
    {
        "rank": 6,
        "name": "Changdeokgung Palace",
        "korean": "창덕궁",
        "lat": 37.5794,
        "lon": 126.9910,
        "category": "Palace",
        "description": "A UNESCO World Heritage site known for its architecture."
    },
    {
        "rank": 7,
        "name": "Insadong",
        "korean": "인사동",
        "lat": 37.5743,
        "lon": 126.9857,
        "category": "Culture",
        "description": "Discover traditional crafts, tea houses and souvenirs."
    },
    {
        "rank": 8,
        "name": "Gwangjang Market",
        "korean": "광장시장",
        "lat": 37.5701,
        "lon": 126.9997,
        "category": "Food Market",
        "description": "A traditional market famous for Korean street food."
    },
    {
        "rank": 9,
        "name": "Hongdae",
        "korean": "홍대",
        "lat": 37.5563,
        "lon": 126.9236,
        "category": "Culture",
        "description": "A lively area known for street performances and shops."
    },
    {
        "rank": 10,
        "name": "Dongdaemun Design Plaza",
        "korean": "동대문디자인플라자",
        "lat": 37.5671,
        "lon": 127.0095,
        "category": "Architecture",
        "description": "A landmark for contemporary design, exhibitions and events."
    }
]

# 사이드바 필터
st.sidebar.header("🔎 Find Attractions")

categories = sorted(set(
    place["category"] for place in attractions
))

selected_categories = st.sidebar.multiselect(
    "Attraction category",
    categories,
    default=categories
)

search = st.sidebar.text_input(
    "Search attractions",
    placeholder="Enter a name or keyword"
).strip().lower()

# 검색 및 필터링
filtered = [
    place for place in attractions
    if place["category"] in selected_categories
    and (
        not search
        or search in place["name"].lower()
        or search in place["korean"].lower()
        or search in place["description"].lower()
        or search in place["category"].lower()
    )
]

col1, col2 = st.columns(2)
col1.metric("Attractions shown", len(filtered))
col2.metric("Total attractions", len(attractions))

# 지도 생성
if filtered:
    m = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=12,
        tiles="OpenStreetMap",
        control_scale=True
    )

    colors = [
        "red", "purple", "blue", "green", "orange",
        "darkred", "cadetblue", "darkgreen", "pink", "darkblue"
    ]

    for place in filtered:
        google_maps_url = (
            "https://www.google.com/maps/search/?api=1&query="
            f"{place['lat']},{place['lon']}"
        )

        popup_html = f"""
        <div style="width:240px;font-family:Arial;">
            <h3>{place['rank']}. {place['name']}</h3>
            <b>{place['korean']}</b>
            <p><b>Category:</b> {place['category']}</p>
            <p>{place['description']}</p>
            <a href="{google_maps_url}" target="_blank">
                Open in Google Maps
            </a>
        </div>
        """

        folium.Marker(
            location=[place["lat"], place["lon"]],
            tooltip=f"{place['rank']}. {place['name']}",
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(
                color=colors[place["rank"] - 1],
                icon="info-sign"
            )
        ).add_to(m)

    st.subheader("📍 Interactive Tourist Map")

    st_folium(
        m,
        use_container_width=True,
        height=600,
        returned_objects=[]
    )

    st.subheader("📋 Tourist Attractions")

    for place in filtered:
        with st.expander(
            f"{place['rank']}. {place['name']} / {place['korean']}"
        ):
            st.write("**Category:**", place["category"])
            st.write(place["description"])

            st.link_button(
                "Open in Google Maps",
                "https://www.google.com/maps/search/?api=1&query="
                f"{place['lat']},{place['lon']}"
            )
else:
    st.warning("No attractions found. Try another search.")

st.markdown("---")
st.caption(
    "This is a curated list of well-known Seoul attractions, "
    "not an official real-time popularity ranking. "
    "Check venue information before visiting."
)
```

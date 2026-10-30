import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Seoul Tourist Map",
    page_icon="🗺️",
    layout="wide"
)

st.title("Seoul Top 10 Tourist Attractions")
st.write("Explore Seoul's famous attractions on the map.")

# Tourist attraction data
places = [
    ("Gyeongbokgung Palace", "경복궁", 37.5796, 126.9770),
    ("N Seoul Tower", "N서울타워", 37.5512, 126.9882),
    ("Bukchon Hanok Village", "북촌한옥마을", 37.5826, 126.9830),
    ("Myeongdong", "명동", 37.5636, 126.9869),
    ("Namsan Park", "남산공원", 37.5503, 126.9900),
    ("Changdeokgung Palace", "창덕궁", 37.5794, 126.9910),
    ("Insadong", "인사동", 37.5743, 126.9857),
    ("Gwangjang Market", "광장시장", 37.5701, 126.9997),
    ("Hongdae", "홍대", 37.5563, 126.9236),
    ("Dongdaemun Design Plaza", "동대문디자인플라자", 37.5671, 127.0095),
]

# Search
search = st.text_input(
    "Search attractions",
    placeholder="Enter an English or Korean name"
).strip().lower()

filtered_places = [
    place for place in places
    if search == ""
    or search in place[0].lower()
    or search in place[1].lower()
]

st.metric("Attractions found", len(filtered_places))

# Create map
if filtered_places:
    tourist_map = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=12,
        tiles="OpenStreetMap"
    )

    for index, place in enumerate(filtered_places, start=1):
        name_en, name_ko, latitude, longitude = place

        google_maps_url = (
            "https://www.google.com/maps/search/?api=1&query="
            f"{latitude},{longitude}"
        )

        popup_html = (
            f"<b>{name_en}</b><br>"
            f"{name_ko}<br><br>"
            f'<a href="{google_maps_url}" target="_blank">'
            "Open in Google Maps</a>"
        )

        folium.Marker(
            location=[latitude, longitude],
            tooltip=name_en,
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(tourist_map)

    st.subheader("Interactive Map")

    st_folium(
        tourist_map,
        use_container_width=True,
        height=600,
        returned_objects=[]
    )

    st.subheader("Tourist Attraction List")

    for place in filtered_places:
        st.write(f"📍 {place[0]} — {place[1]}")

else:
    st.info("No attractions found. Try another search.")

st.caption(
    "This is a curated list of popular Seoul attractions, "
    "not an official popularity ranking."
)

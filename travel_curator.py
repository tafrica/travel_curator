import streamlit as st
from datetime import date
from io import BytesIO

st.set_page_config(page_title="Your Personalized Travel Curator", page_icon="🌍")
st.title("🌍 Your Personalized Travel Curator (Safe Layout Mode)")

# --- Inputs ---
ideal_trip = st.text_area(
    "Describe your ideal vacation or a past trip you loved:",
    placeholder="Example: I loved my hiking trip in Patagonia with local food and boutique hotels.",
)

destination = st.text_input(
    "Where are you thinking of going next?",
    placeholder="Example: Denver and Aspen, Colorado",
)

start_date = st.date_input("When will your trip start?", value=date.today())
num_days = st.slider("How many days should I plan for?", 1, 7, 3)

# --- Sample Multi-Day Itinerary ---
SAMPLE_ITINERARY_DAYS = [
    {
        "title": "Day 1: Arrival in Denver",
        "main": "☀️ Morning: Arrive in Denver International Airport, check into your hotel.\n\n"
                "🌄 Afternoon: Visit the Denver Art Museum — currently featuring a Monet exhibition.\n\n"
                "🌙 Evening: Dinner at Linger — a rooftop restaurant with live jazz music.",
        "extra": "**Extra Details:**\n- Reading: The History of Denver's Art Scene."
    },
    {
        "title": "Day 2: Explore the Rockies",
        "main": "☀️ Morning: Drive to Rocky Mountain National Park for scenic hikes.\n\n"
                "🌄 Afternoon: Picnic with views of Longs Peak.\n\n"
                "🌙 Evening: Return to Denver for a craft beer tasting tour.",
        "extra": "**Extra Details:**\n- Playlist: Road Trip Colorado Vibes."
    }
]

# --- Generate Itinerary ---
if st.button("Generate My Trip Ideas"):
    if not ideal_trip or not destination:
        st.warning("Please enter both a vacation description and a destination.")
    else:
        st.write("### Your Curated Itinerary")
        for day in SAMPLE_ITINERARY_DAYS:
            with st.expander(day["title"]):
                st.markdown(day["main"])
                st.markdown(day["extra"])

        # --- Download Button ---
        itinerary_content = ""
        for day in SAMPLE_ITINERARY_DAYS:
            itinerary_content += f"<h2>{day['title']}</h2><p>{day['main'].replace('\n', '<br>')}</p><p>{day['extra'].replace('\n', '<br>')}</p><br><br>"
        html_output = f"<html><head><meta charset='UTF-8'><title>Travel Itinerary</title></head><body><h1>Itinerary for {destination}</h1>{itinerary_content}</body></html>"
        html_bytes = BytesIO(html_output.encode("utf-8"))
        st.download_button(
            label="📥 Download Itinerary as HTML",
            data=html_bytes,
            file_name="travel_itinerary.html",
            mime="text/html"
        )

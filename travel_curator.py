import streamlit as st
from datetime import date

st.set_page_config(page_title="Your Personalized Travel Curator", page_icon="🌍")
st.title("🌍 Your Personalized Travel Curator (Safe Mode)")

st.write("DEBUG: Safe Base Version Loaded")

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

# --- Sample Data ---
SAMPLE_ITINERARY = """Day 1: Arrival in Denver
☀️ Morning: Arrive in Denver International Airport, check into your hotel.
🌄 Afternoon: Visit the Denver Art Museum — currently featuring a Monet exhibition.
🌙 Evening: Dinner at Linger — a rooftop restaurant with live jazz music.

**Extra Details:**
- Reading: The History of Denver's Art Scene.
"""

# --- Generate Itinerary ---
if st.button("Generate My Trip Ideas"):
    if not ideal_trip or not destination:
        st.warning("Please enter both a vacation description and a destination.")
    else:
        st.write("### Your Curated Itinerary")
        st.markdown(SAMPLE_ITINERARY)

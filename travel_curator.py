import streamlit as st
from datetime import date
from io import BytesIO
import os

from openai import OpenAI

st.set_page_config(page_title="Your Personalized Travel Curator", page_icon="🌍")
st.title("🌍 Your Personalized Travel Curator (OpenAI Safe Mode)")

# --- Test Mode ---
use_test_mode = st.sidebar.checkbox("Use Test Mode (No API calls)", value=True)
client = None

if not use_test_mode:
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.warning("⚠️ OpenAI API key not found. Running in Test Mode.")
        use_test_mode = True
    else:
        try:
            client = OpenAI(api_key=api_key)
            st.write("DEBUG: OpenAI client initialized")
        except Exception as e:
            st.error(f"Failed to initialize OpenAI: {e}")
            use_test_mode = True

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
SAMPLE_ITINERARY = """Day 1: Arrival in Denver
☀️ Morning: Arrive in Denver International Airport, check into your hotel.
🌄 Afternoon: Visit the Denver Art Museum — currently featuring a Monet exhibition.
🌙 Evening: Dinner at Linger — a rooftop restaurant with live jazz music.

**Extra Details:**
- Reading: The History of Denver's Art Scene.
"""

def build_prompt():
    return f"""You are a creative travel planner. Your goal is to create itineraries that feel curated, personal, and full of cultural depth.

For every restaurant, activity, or attraction:
- Use the official website if available.
- If an additional trusted source is found (like TripAdvisor, a reputable travel blog, or a review site), add it as a second link.
- If no official site exists, use a Google Maps search link (e.g., [Place Name](https://www.google.com/maps/search/Place+Name)).
- Do not fabricate URLs. If nothing is found, simply list the activity name without a link.

After listing morning, afternoon, and evening activities for each day, ALWAYS include an "**Extra Details:**" section.
- This section should enrich the travel experience with:
  - A link to a relevant article, blog, or resource for context.
  - If applicable, a current exhibit, seasonal highlight, or cultural insight.

Never skip Extra Details or links — create them even if you have to search generically.

Destination: {destination}
Trip duration: {num_days} days starting {start_date}.
Traveler preferences: {ideal_trip}"""

# --- Generate Itinerary ---

if st.checkbox("Show Prompt Preview"):
    st.code(build_prompt(), language="markdown")

if st.button("Generate My Trip Ideas"):
    if not ideal_trip or not destination:
        st.warning("Please enter both a vacation description and a destination.")
    else:
        st.write("### Your Curated Itinerary")
        raw_text = SAMPLE_ITINERARY
        if not use_test_mode and client:
            with st.spinner("Creating your personalized itinerary..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a travel planner who creates detailed itineraries with links and cultural extras."},
                            {"role": "user", "content": build_prompt()},
                        ],
                        temperature=0.8
                    )
                    raw_text = response.choices[0].message.content.strip()
                except Exception as e:
                    st.error(f"Error generating itinerary: {e}")
                    raw_text = SAMPLE_ITINERARY

        st.markdown(raw_text)

        # --- Download Button ---
        html_output = f"<html><head><meta charset='UTF-8'><title>Travel Itinerary</title></head><body><h1>Itinerary for {destination}</h1><p>{raw_text.replace('\n', '<br>')}</p></body></html>"
        html_bytes = BytesIO(html_output.encode("utf-8"))
        st.download_button(
            label="📥 Download Itinerary as HTML",
            data=html_bytes,
            file_name="travel_itinerary.html",
            mime="text/html"
        )

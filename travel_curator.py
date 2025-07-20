import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import date
import re

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Your Personalized Travel Curator", page_icon="🌍")

st.title("🌍 Your Personalized Travel Curator")
st.write(
    "Tell me about your favorite trip (or dream vacation), and I'll generate a customized itinerary "
    "with activities, dining ideas, links to more info, and current events tailored to your style."
)

# --- User Inputs ---
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

def add_google_maps_links(text):
    def linkify_place(match):
        place = match.group(0)
        query = place.replace(" ", "+")
        return f"[{place}](https://www.google.com/maps/search/?api=1&query={query})"
    return re.sub(r'\b([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*)\b', linkify_place, text)

def split_by_days(text):
    # Split on '### Day' to isolate each day
    days = re.split(r'(### Day \d+:)', text)
    combined = []
    for i in range(1, len(days), 2):
        combined.append(days[i] + days[i + 1])
    return combined

# --- Button to Generate ---
if st.button("Generate My Trip Ideas"):
    if not ideal_trip or not destination:
        st.warning("Please enter both a vacation description and a destination.")
    else:
        with st.spinner("Creating your personalized itinerary..."):
            prompt = f"""
            You are a travel expert. Based on the following user's preferences:
            "{ideal_trip}"
            Create a {num_days}-day itinerary for {destination}, starting {start_date}.

            Important formatting instructions:
            - Begin the itinerary immediately with '### Day 1: ...' (no introduction or extra text).
            - Use **only Markdown headings and bullet points** (no HTML tags).
            - Title each day as a Markdown heading, e.g., '### Day 1: Arrival in Denver'.
            - Use bullet points for morning, afternoon, and evening activities with emojis (☀️, 🌇, 🌙).
            - Add clickable Markdown links for restaurants, tours, or places of interest.
            - Do not add text like 'Copy or Download' or any conclusion text.
            """

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a friendly and creative travel planner who formats itineraries using pure Markdown."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7
                )
                itinerary_text = response.choices[0].message.content
                itinerary_text = add_google_maps_links(itinerary_text)

                days = split_by_days(itinerary_text)
                if not days:
                    st.markdown(itinerary_text)
                else:
                    for day in days:
                        lines = day.splitlines()
                        day_title = lines[0].replace("### ", "")
                        content = "\n".join(lines[1:])
                        with st.expander(day_title.strip()):
                            st.markdown(content)

            except Exception as e:
                st.error(f"Error generating itinerary: {e}")

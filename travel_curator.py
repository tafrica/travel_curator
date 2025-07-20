import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import date
import re

# --- CONFIG ---
# Toggle for test mode
use_test_mode = st.sidebar.checkbox("Use Test Mode (No API calls)", value=True)

if not use_test_mode:
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Your Personalized Travel Curator", page_icon="🌍")

st.title("🌍 Your Personalized Travel Curator")

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

STOPWORDS = {"Day", "Morning", "Afternoon", "Evening", "Arrival", "Breakfast", "Lunch", "Dinner", "Exploration", "Hotel"}

def link_line(line):
    stripped = line.strip()
    if stripped.startswith("###") or stripped.startswith("Day") or stripped.startswith(("☀️", "🌇", "🌙")):
        return line
    if "[" in line and "](" in line:
        return line

    def replacer(match):
        phrase = match.group(0)
        if " " not in phrase:
            return phrase
        if phrase.split()[0] in STOPWORDS:
            return phrase
        return f"[{phrase}](https://www.google.com/maps/search/?api=1&query={phrase.replace(' ', '+')})"

    return re.sub(r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)+)\b', replacer, line)

def add_google_maps_links(text):
    lines = text.splitlines()
    linked_lines = [link_line(line) for line in lines]
    return "\n".join(linked_lines)

def ensure_extra_details(day_text):
    if "**Extra Details:**" not in day_text:
        day_text += "\n\n**Extra Details:**\n- (No extra details provided by AI)"
    return day_text

def clean_to_days(text):
    days = re.split(r'(?:###?\s*)?(Day \d+:)', text)
    combined = []
    for i in range(1, len(days), 2):
        content = days[i] + days[i + 1]
        combined.append(ensure_extra_details(content))
    if not combined:
        combined = [ensure_extra_details(text)]
    return combined

# --- TEST DATA ---
SAMPLE_ITINERARY = """Day 1: Arrival in Denver (2025-07-28)
☀️ Morning: Arrive in Denver, check into your hotel.
🌄 Afternoon: Visit the Denver Art Museum — currently featuring a Monet exhibition.
🌙 Evening: Dinner at Linger — a rooftop restaurant with live jazz music.

**Extra Details:**
- **Reading:** "The History of Denver's Art Scene" (Denver Post).
- **Playlist:** "Summer Vibes in Colorado" on Spotify.

Day 2: Exploring the Rockies
☀️ Morning: Guided hike at Red Rocks Park.
🌄 Afternoon: Picnic near Bear Creek and visit geological formations.
🌙 Evening: Concert at Red Rocks Amphitheatre (check schedule).

**Extra Details:**
- **Reading:** "Colorado's Natural Wonders".
- **Music:** Iconic live sets recorded at Red Rocks.

Day 3: Aspen Adventure
☀️ Morning: Drive to Aspen via Independence Pass.
🌄 Afternoon: Explore the Aspen Art Museum and boutiques.
🌙 Evening: Dinner at White House Tavern — known for craft cocktails.

**Extra Details:**
- **Reading:** "Aspen’s Cultural Renaissance".
- **Playlist:** Smooth Jazz Evenings in Aspen (Spotify).

Day 4: Outdoor Thrills
☀️ Morning: Go mountain biking in Snowmass Village.
🌄 Afternoon: Relax at Glenwood Hot Springs.
🌙 Evening: Dine at Cache Cache — renowned for French cuisine.

**Extra Details:**
- **Reading:** "Colorado's Best Hot Springs".
- **Playlist:** Adventure Beats on Spotify.

Day 5: Farewell Day
☀️ Morning: Brunch at Snooze, an A.M. Eatery.
🌄 Afternoon: Last-minute shopping at Larimer Square.
🌙 Evening: Sunset walk at City Park before heading home.

**Extra Details:**
- **Reading:** "Denver's Top Brunch Spots".
- **Playlist:** Relaxing Acoustic Mix.
"""

# --- Button ---
if st.button("Generate My Trip Ideas"):
    if not ideal_trip or not destination:
        st.warning("Please enter both a vacation description and a destination.")
    else:
        if use_test_mode:
            raw_text = SAMPLE_ITINERARY
        else:
            with st.spinner("Creating your personalized itinerary..."):
                prompt = f""" 
                You are a travel expert. Based on the following user's preferences:
                "{ideal_trip}"
                Create a {num_days}-day itinerary for {destination}, starting {start_date}.

                Formatting rules:
                - Start the response directly with 'Day 1: ...' (no intro or conclusion).
                - Use Markdown headings for each day (Day X: ...).
                - Use bullet points for morning, afternoon, and evening activities with emojis (☀️, 🌇, 🌙).
                - Add clickable Markdown links for specific restaurants, tours, or places of interest (but NOT for generic words like Morning, Afternoon, Evening).
                - After the activities for each day, ALWAYS include an "**Extra Details:**" section with:
                  - Info on current exhibits/events at cultural spots.
                  - A recommended article/book for context.
                  - A playlist or music suggestion that matches the vibe.
                - Do not include any extra text like 'Copy or Download Your Itinerary'.
                """ 

                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a creative travel planner who formats itineraries with Markdown and adds cultural context."},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.8
                    )
                    raw_text = response.choices[0].message.content
                except Exception as e:
                    st.error(f"Error generating itinerary: {e}")
                    raw_text = ""

        if raw_text:
            raw_text = add_google_maps_links(raw_text)
            days = clean_to_days(raw_text)
            for day in days:
                lines = day.splitlines()
                if not lines:
                    continue
                day_title = lines[0]
                content = "\n".join(lines[1:])
                with st.expander(day_title.strip()):
                    st.markdown(content)

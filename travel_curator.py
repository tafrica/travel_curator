import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import date
import re
import urllib.parse

# --- CONFIG ---
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

def ensure_extra_details(day_text):
    if "**Extra Details:**" not in day_text:
        day_text += "\n\n**Extra Details:**\n"
        day_text += "- [Explore the destination on Google](https://www.google.com/search?q=" + urllib.parse.quote(destination) + ")\n"
        day_text += "- [Listen to a themed playlist](https://open.spotify.com/search/" + urllib.parse.quote(destination) + ")"
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

def auto_link_missing(content):
    def replacer(match):
        phrase = match.group(0)
        if "[" in phrase or "Day" in phrase or phrase in ["Morning", "Afternoon", "Evening"]:
            return phrase
        return f"[{phrase}](https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(phrase)})"

    lines = content.split("\n")
    new_lines = []
    for line in lines:
        if line.startswith(("☀️", "🌇", "🌙")) and "[" not in line:
            line = re.sub(r'([A-Z][a-z]+(?: [A-Z][a-z]+)+)', replacer, line)
        new_lines.append(line)
    return "\n".join(new_lines)

# --- TEST DATA ---
SAMPLE_ITINERARY = """Day 1: Arrival in Denver (2025-07-28)
☀️ Morning: Arrive in [Denver International Airport](https://www.flydenver.com/), check into your hotel.
🌄 Afternoon: Visit the [Denver Art Museum](https://denverartmuseum.org/) — currently featuring a Monet exhibition.
🌙 Evening: Dinner at [Linger](https://www.lingerdenver.com/) — a rooftop restaurant with live jazz music.

**Extra Details:**
- **Reading:** [The History of Denver's Art Scene](https://www.google.com/search?q=The+History+of+Denver's+Art+Scene).
- **Playlist:** [Summer Vibes in Colorado](https://open.spotify.com/playlist/37i9dQZF1DX0h0QnOySuGd).
"""

# --- Build Prompt ---
def build_prompt():
    return f""" 
    You are a creative travel planner. Your goal is to create itineraries that feel curated, personal, and full of cultural depth.

    1. For every restaurant, activity, or attraction, ALWAYS include a clickable Markdown link to a reputable site or Google Maps.
    2. After listing morning, afternoon, and evening activities for each day, ALWAYS include an "**Extra Details:**" section.
       - This section should enrich the travel experience with:
         - A link to a relevant article, blog, or resource for context.
         - A playlist or music suggestion that matches the vibe (with a clickable link).
         - If applicable, a current exhibit, seasonal highlight, or cultural insight.
    3. If real-time info is not available, invent realistic, helpful details.
    4. Never skip Extra Details or links — create them even if you have to search generically.

    Destination: {destination}
    Trip duration: {num_days} days starting {start_date}.
    Traveler preferences: {ideal_trip}

    Format the itinerary like this example:

    Day 1: Arrival in Denver (2025-07-28)
    ☀️ Morning: Arrive at [Denver International Airport](https://www.flydenver.com/), check into [The Crawford Hotel](https://thecrawfordhotel.com/).
    🌄 Afternoon: Visit the [Denver Art Museum](https://denverartmuseum.org/) — see the Monet exhibition.
    🌙 Evening: Dinner at [Linger](https://www.lingerdenver.com/) — rooftop dining with live jazz.

    **Extra Details:**
    - **Reading:** [The History of Denver’s Art Scene](https://www.google.com/search?q=History+of+Denver's+Art+Scene).
    - **Playlist:** [Colorado Summer Vibes on Spotify](https://open.spotify.com/playlist/37i9dQZF1DX0h0QnOySuGd).
    - **Cultural Highlight:** Evening jazz concerts on the rooftop.
    """

# --- Prompt Preview ---
with st.expander("🔍 Preview the AI Prompt"):
    st.markdown(f"```
{build_prompt()}
```")

# --- Generate Itinerary ---
if st.button("Generate My Trip Ideas"):
    if not ideal_trip or not destination:
        st.warning("Please enter both a vacation description and a destination.")
    else:
        if use_test_mode:
            raw_text = SAMPLE_ITINERARY
        else:
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
                    raw_text = response.choices[0].message.content
                except Exception as e:
                    st.error(f"Error generating itinerary: {e}")
                    raw_text = ""

        if raw_text:
            days = clean_to_days(raw_text)
            for day in days:
                lines = day.splitlines()
                if not lines:
                    continue
                day_title = lines[0]
                content = "\n".join(lines[1:])
                content = auto_link_missing(content)
                with st.expander(day_title.strip()):
                    st.markdown(content)

import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import date
import re
import urllib.parse
from io import BytesIO

# --- CONFIG ---
use_test_mode = st.sidebar.checkbox("Use Test Mode (No API calls)", value=True)
inspiration_mode = st.sidebar.checkbox("Enable Inspiration Mode (show alternatives)", value=False)

if not use_test_mode:
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Your Personalized Travel Curator", page_icon="🌍")

st.title("🌍 Your Personalized Travel Curator")

# Initialize session state
if "itinerary_days" not in st.session_state:
    st.session_state.itinerary_days = []

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

def regenerate_extra_details(day_index, day_title):
    if use_test_mode:
        st.session_state.itinerary_days[day_index]["extra"] = "**Extra Details (Updated):**\n- [Sample Article](https://www.google.com)\n- [Sample Playlist](https://open.spotify.com)"
    else:
        try:
            prompt = f"Generate 2 cultural or music recommendations for {day_title} in {destination}. Return them as markdown list with links."
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You add cultural and music details."},
                          {"role": "user", "content": prompt}],
                temperature=0.7
            )
            st.session_state.itinerary_days[day_index]["extra"] = response.choices[0].message.content.strip()
        except Exception as e:
            st.session_state.itinerary_days[day_index]["extra"] = f"**Extra Details:** (Failed to regenerate: {e})"

def add_inspiration_ideas(content, day_title):
    if use_test_mode:
        return content + "\n\n**Inspiration Mode:**\n- Alternative 1 for " + day_title + "\n- Alternative 2 for " + day_title
    else:
        try:
            prompt = f"Suggest 2 alternative activities each for morning, afternoon, and evening of {day_title} in {destination}. Return in markdown list format."
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You provide alternative travel activity ideas."},
                          {"role": "user", "content": prompt}],
                temperature=0.8
            )
            return content + "\n\n**Inspiration Mode:**\n" + response.choices[0].message.content.strip()
        except Exception as e:
            return content + f"\n\n**Inspiration Mode:** (Failed to load: {e})"

# --- TEST DATA ---
SAMPLE_ITINERARY = """Day 1: Arrival in Denver (2025-07-28)
☀️ Morning: Arrive in [Denver International Airport](https://www.flydenver.com/), check into your hotel.
🌄 Afternoon: Visit the [Denver Art Museum](https://denverartmuseum.org/) — currently featuring a Monet exhibition.
🌙 Evening: Dinner at [Linger](https://www.lingerdenver.com/) — a rooftop restaurant with live jazz music.

**Extra Details:**
- **Reading:** [The History of Denver's Art Scene](https://www.google.com/search?q=The+History+of+Denver's+Art+Scene).
- **Playlist:** [Summer Vibes in Colorado](https://open.spotify.com/playlist/37i9dQZF1DX0h0QnOySuGd).
"""

def build_prompt():
    base_prompt = f"""
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
"""
    if inspiration_mode:
        base_prompt += "\n5. Provide 2-3 alternative activities for each time slot (Morning, Afternoon, Evening) as an 'Inspiration Mode' list.\n"
    return base_prompt

if st.checkbox("Show Prompt Preview"):
    st.code(build_prompt(), language="markdown")

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
            st.session_state.itinerary_days = []
            days = clean_to_days(raw_text)
            for day in days:
                lines = day.splitlines()
                if not lines:
                    continue
                day_title = lines[0]
                content = "\n".join(lines[1:])
                content = auto_link_missing(content)

                if inspiration_mode:
                    content = add_inspiration_ideas(content, day_title)

                if "**Extra Details:**" in content:
                    main_content, extra = content.split("**Extra Details:**", 1)
                    extra_details = "**Extra Details:**" + extra
                else:
                    main_content = content
                    extra_details = "**Extra Details:** (none)"

                st.session_state.itinerary_days.append({
                    "title": day_title.strip(),
                    "main": main_content,
                    "extra": extra_details
                })

# --- Display Itinerary ---
if st.session_state.itinerary_days:
    for i, day_data in enumerate(st.session_state.itinerary_days):
        with st.expander(day_data["title"]):
            st.markdown(day_data["main"])
            st.markdown(day_data["extra"])
            if st.button(f"🔄 Regenerate Extra Details for {day_data['title']}", key=f"regen_{i}"):
                regenerate_extra_details(i, day_data["title"])

    itinerary_content = ""
    for day_data in st.session_state.itinerary_days:
        itinerary_content += f"<h2>{day_data['title']}</h2><p>{day_data['main'].replace('\n', '<br>')}</p><p>{day_data['extra'].replace('\n', '<br>')}</p><br><br>"
    html_output = f"<html><head><meta charset='UTF-8'><title>Travel Itinerary</title></head><body><h1>Itinerary for {destination}</h1>{itinerary_content}</body></html>"
    html_bytes = BytesIO(html_output.encode("utf-8"))
    st.download_button(
        label="📥 Download Itinerary as HTML",
        data=html_bytes,
        file_name="travel_itinerary.html",
        mime="text/html"
    )

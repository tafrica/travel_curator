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

STOPWORDS = {"Day", "Morning", "Afternoon", "Evening", "Arrival", "Breakfast", "Lunch", "Dinner", "Exploration"}

def link_line(line):
    # Skip headings or lines with emojis
    if line.strip().startswith("###") or line.strip().startswith(("☀️", "🌇", "🌙")):
        return line
    # Skip lines already containing markdown links
    if "[" in line and "](" in line:
        return line

    def replacer(match):
        phrase = match.group(0)
        if phrase.split()[0] in STOPWORDS:
            return phrase
        return f"[{phrase}](https://www.google.com/maps/search/?api=1&query={phrase.replace(' ', '+')})"

    # Only link multi-word capitalized phrases
    return re.sub(r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)+)\b', replacer, line)

def add_google_maps_links(text):
    lines = text.splitlines()
    linked_lines = [link_line(line) for line in lines]
    return "\n".join(linked_lines)

def clean_to_days(text):
    match = re.search(r'(### Day 1.*)', text, flags=re.DOTALL)
    text = match.group(1) if match else text
    days = re.split(r'(### Day \d+:)', text)
    combined = []
    for i in range(1, len(days), 2):
        combined.append(days[i] + days[i + 1])
    return combined if combined else [text]

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

            Formatting rules:
            - Start the response directly with '### Day 1: ...' (no intro or conclusion).
            - Use Markdown headings for each day (### Day X: ...).
            - Use bullet points for morning, afternoon, and evening activities with emojis (☀️, 🌇, 🌙).
            - Add clickable Markdown links for specific restaurants, tours, or places of interest (but NOT for generic words like Morning, Afternoon, Evening).
            - Include current events/exhibits where relevant.
            - Do not include any extra text like 'Copy or Download Your Itinerary'.
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
                raw_text = response.choices[0].message.content
                raw_text = add_google_maps_links(raw_text)
                days = clean_to_days(raw_text)

                for day in days:
                    lines = day.splitlines()
                    if not lines:
                        continue
                    day_title = lines[0].replace("### ", "")
                    content = "\n".join(lines[1:])
                    with st.expander(day_title.strip()):
                        st.markdown(content)

            except Exception as e:
                st.error(f"Error generating itinerary: {e}")

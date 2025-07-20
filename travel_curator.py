import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import date
import re
import urllib.parse

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

itinerary_text = ""

def add_google_maps_links(text):
    def linkify_place(match):
        place = match.group(0)
        query = place.replace(" ", "+")
        return f"[{place}](https://www.google.com/maps/search/?api=1&query={query})"
    return re.sub(r'\b([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*)\b', linkify_place, text)

def extract_places_for_day(day_text):
    places = re.findall(r'\b([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*)\b', day_text)
    unique_places = list(dict.fromkeys(places))
    return unique_places

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

            For each day:
            - Title each day clearly (Day 1, Day 2, etc.).
            - Use emojis to highlight Morning (☀️), Afternoon (🌇), and Evening (🌙).
            - Include at least one unique restaurant or dining experience per day.
            - Add clickable markdown links for restaurants, tours, or places of interest.
            - If there are museums or cultural venues, include current exhibits/events during the travel dates.
            - Format the response with markdown so that each day is easy to separate.
            """

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a friendly and creative travel planner who formats itineraries with collapsible sections and emojis."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7
                )
                itinerary_text = response.choices[0].message.content
                itinerary_text = add_google_maps_links(itinerary_text)

                days = itinerary_text.split("Day ")
                for i, day in enumerate(days):
                    if day.strip():
                        if i == 0 and "Day" not in day:
                            st.markdown(day.strip())
                        else:
                            day_title = day.splitlines()[0]
                            day_content = "Day " + day
                            with st.expander(f"Day {day_title}"):
                                st.markdown(day_content)
                                places = extract_places_for_day(day_content)
                                if places:
                                    query = urllib.parse.quote_plus(" ".join(places))
                                    maps_url = f"https://www.google.com/maps/search/{query}"
                                    st.markdown(f"[View All on Google Maps]({maps_url})")

            except Exception as e:
                st.error(f"Error generating itinerary: {e}")

# --- Copy & Download ---
if itinerary_text:
    st.write("### Copy or Download Your Itinerary")
    st.code(itinerary_text, language="markdown")
    st.button("Copy Itinerary", on_click=lambda: st.write("Select and copy the text above."))

    # Download as text
    st.download_button(
        label="Download as Text",
        data=itinerary_text,
        file_name="itinerary.txt",
        mime="text/plain",
    )

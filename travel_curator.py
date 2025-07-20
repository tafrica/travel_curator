import streamlit as st
import openai
import os

st.set_page_config(page_title="Your Personalized Travel Curator", page_icon="🌍")

st.title("🌍 Your Personalized Travel Curator")
st.write(
    "Tell me about your favorite trip (or dream vacation), and I'll generate a customized itinerary "
    "with activities and dining ideas tailored to your style."
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

num_days = st.slider("How many days should I plan for?", 1, 7, 3)

# --- Button to Generate ---
if st.button("Generate My Trip Ideas"):
    if not ideal_trip or not destination:
        st.warning("Please enter both a vacation description and a destination.")
    else:
        with st.spinner("Creating your personalized itinerary..."):
            prompt = f"""
            You are a travel expert. Based on the following user's preferences:
            "{ideal_trip}"
            Create a {num_days}-day itinerary for {destination}, including:
            - Morning, afternoon, and evening activities.
            - At least one unique restaurant or dining experience per day.
            - Short, exciting descriptions that feel personal and curated.
            """

            try:
                openai.api_key = os.getenv("OPENAI_API_KEY")
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a friendly and creative travel planner."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7
                )
                itinerary = response['choices'][0]['message']['content']
                st.markdown(itinerary)
            except Exception as e:
                st.error(f"Error generating itinerary: {e}")

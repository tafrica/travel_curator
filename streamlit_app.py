import streamlit as st
from travel_curator import generate_itinerary

st.set_page_config(page_title="Travel Curator", page_icon="🌍", layout="centered")

st.title("🌍 Travel Curator")
st.markdown("Plan your day like a local! Enter your destination and preferences below:")

destination = st.text_input("Destination", "Madrid")
preferences = st.text_area("Preferences", "See as many cats as possible, enjoy good food, and find swimming spots.")

if st.button("Generate Itinerary"):
    if destination.strip():
        st.write("### Your Curated Itinerary")
        with st.spinner("Generating your itinerary..."):
            try:
                itinerary = generate_itinerary(destination.strip(), preferences.strip())
                st.write(itinerary)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a destination.")

import streamlit as st
from travel_curator_fixed import generate_itinerary

# Configure page
st.set_page_config(page_title="Travel Curator", page_icon="🌍", layout="centered")

# Debug banner
st.write("### DEBUG: app.py is running")

st.title("🌍 Travel Curator")
st.markdown("Plan your day like a local! Enter your destination and preferences below:")

# Pre-filled example values for testing
destination = st.text_input("Destination", "Madrid")
preferences = st.text_area("Preferences", "See as many cats as possible, enjoy good food, and find swimming spots.")

# Generate button
if st.button("Generate Itinerary"):
    if destination.strip():
        st.write("### Your Curated Itinerary")
        try:
            itinerary = generate_itinerary(destination.strip(), preferences.strip())
            st.write(itinerary)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a destination.")

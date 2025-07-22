import streamlit as st
from travel_curator_fixed import generate_itinerary

st.set_page_config(page_title="Travel Curator", page_icon="🌍", layout="centered")

st.title("🌍 Travel Curator")
st.markdown("Plan your day like a local! Enter your destination and preferences below:")

# Input fields
destination = st.text_input("Destination", placeholder="e.g., Madrid")
preferences = st.text_area("Preferences", placeholder="e.g., See as many cats as possible, enjoy good food, and find swimming spots.")

# Generate button
if st.button("Generate Itinerary"):
    if destination.strip():
        st.write("### Your Curated Itinerary")
        itinerary = generate_itinerary(destination.strip(), preferences.strip())
        st.write(itinerary)
    else:
        st.warning("Please enter a destination.")

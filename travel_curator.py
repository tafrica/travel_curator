import streamlit as st
import openai
import re
from travel_tools import search_activities

openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

st.title("AI Travel Curator")

# Main inputs
destination = st.text_input("Enter your destination:")
start_date = st.date_input("Trip start date:")
days = st.number_input("Number of days:", min_value=1, max_value=30, value=1)
vacation_description = st.text_area("Tell us about a vacation you loved (to help personalize your trip):")

# Sidebar options
st.sidebar.header("Options")
test_mode = st.sidebar.checkbox("Run in test mode (no API calls)", value=False)
show_prompt = st.sidebar.checkbox("Show final prompt")

def extract_urls(text):
    return re.findall(r'(https?://\S+)', text)

def format_links(text):
    urls = extract_urls(text)
    for url in urls:
        text = text.replace(url, f"[Link]({url})")
    return text

def build_prompt(destination, days, search_context, vacation_description):
    return f"""Create a travel itinerary for {destination} starting on {start_date} for {days} days.
    Tailor recommendations to the type of experiences the user enjoyed: {vacation_description}.
    Use the following verified resources for inspiration:
    {search_context}
    Provide morning, afternoon, and evening plans with a mix of attractions, dining, and activities.
    """

def generate_itinerary(destination, days):
    system_prompt = """You are a travel planning assistant. Use the provided search results
    and user preferences to create a personalized itinerary. 
    Always cite sources with URLs. Avoid inventing details."""

    search_results = search_activities(destination)
    search_context = "\n".join(search_results) if search_results else "No data found."
    user_prompt = build_prompt(destination, days, search_context, vacation_description)

    if show_prompt:
        st.sidebar.subheader("Prompt Preview")
        st.sidebar.text_area("System + User Prompt", system_prompt + "\n\n" + user_prompt, height=300)

    if test_mode:
        return "**TEST MODE:** No API call made.\n\nSample Itinerary:\n- Morning: Visit a landmark.\n- Afternoon: Explore a museum.\n- Evening: Enjoy local cuisine."

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.5,
        max_tokens=1200,
    )

    raw_output = response['choices'][0]['message']['content']
    return format_links(raw_output)

if st.button("Generate My Trip Ideas"):
    if destination:
        with st.spinner("Building your itinerary..."):
            itinerary = generate_itinerary(destination, days)
            st.markdown(itinerary)
    else:
        st.warning("Please enter a destination.")

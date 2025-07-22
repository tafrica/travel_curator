import streamlit as st
from openai import OpenAI
import re
from travel_tools import search_activities

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", ""))

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
    Use ONLY the verified resources provided here:
    {search_context}
    
    **Rules for Output:**
    - Each activity must include a clickable markdown link to a real URL from the search results.
    - If no link is available for an activity, write '(No link found)'.
    - Do not use placeholder text like '(source.)'.
    - Organize activities into Morning, Afternoon, and Evening for each day.
    - Do not invent details or attractions not mentioned in the verified resources.
    """

def generate_itinerary(destination, days):
    system_prompt = """You are a travel planning assistant. Use only the provided search results and user preferences
    to create a personalized itinerary. Always provide real links for each activity. If a link does not exist, clearly indicate '(No link found)'. Avoid invented content."""

    search_results = search_activities(destination)
    search_context = "\n".join(search_results) if search_results else "No data found."
    user_prompt = build_prompt(destination, days, search_context, vacation_description)

    if show_prompt:
        st.sidebar.subheader("Prompt Preview")
        st.sidebar.text_area("System Prompt", system_prompt, height=150)
        st.sidebar.text_area("User Prompt", user_prompt, height=250)

    if test_mode:
        return "**TEST MODE:** No API call made.\n\nSample Itinerary:\n- Morning: Visit a landmark. (No link found)\n- Afternoon: Explore a museum. (No link found)\n- Evening: Enjoy local cuisine. (No link found)"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=1200,
    )

    raw_output = response.choices[0].message.content
    return format_links(raw_output)

if st.button("Generate My Trip Ideas"):
    if destination:
        with st.spinner("Building your itinerary..."):
            itinerary = generate_itinerary(destination, days)
            st.markdown(itinerary)
    else:
        st.warning("Please enter a destination.")

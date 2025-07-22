import streamlit as st
import openai
import re
from travel_tools import search_activities  # Replace with your actual search implementation

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("AI Travel Curator")

destination = st.text_input("Enter your destination:")
days = st.number_input("Number of days:", min_value=1, max_value=30, value=1)

def extract_urls(text):
    # Extracts real URLs from a given text
    return re.findall(r'(https?://\S+)', text)

def format_links(text):
    # Convert any found URLs to clickable markdown links
    urls = extract_urls(text)
    for url in urls:
        text = text.replace(url, f"[Link]({url})")
    return text

def generate_itinerary(destination, days):
    system_prompt = f"""
    You are a precise and reliable travel curator.

    Your task is to create a travel itinerary based only on verified sources. 
    Do not fabricate details, cultural phenomena, or events. Never create fake article references.

    **Search priority:**
    1. Tripadvisor and Viator (activities, attractions, tours).
    2. Reputable travel blogs, travel magazines, and local event calendars.
    3. If none of the above sources return relevant information, clearly say: 
       "No specific recommendations found from trusted sources."

    **Output Requirements:**
    - For every activity, **include a valid clickable URL** to the source (e.g., Tripadvisor or blog link).
    - If no link is available, write: “(No link found)” — do not omit it.
    - Organize the results as a day plan (Morning, Afternoon, Evening).
    - Use only information from the sources retrieved; never invent restaurants, attractions, or descriptions.
    - If the search returns general categories (e.g., “top beaches”), provide the real names and links from those results.
    - Avoid adding any unverified "fun facts" or embellishments.

    **Steps to Follow:**
    1. Search Tripadvisor and Viator for {destination}.
    2. If not enough results, search for recent travel blogs, travel magazines, or local event calendars.
    3. Extract 5–7 recommended activities or places, with URLs.
    4. Build a concise itinerary (Morning/Afternoon/Evening), each with a brief description (1-2 sentences) and a link.
    5. Return results exactly as requested — do not add content beyond verified info.

    **Important Rules:**
    - Never make up sources or details.
    - Always show at least one link per activity or explicitly say “No link found.”
    - If a section of the day has no results, write: “No verified recommendations found for [Morning/Afternoon/Evening].”
    """

    search_results = search_activities(destination)
    search_context = "\n".join(search_results) if search_results else "No data found."

    user_prompt = f"""
    Destination: {destination}
    Days: {days}
    Verified Search Results:
    {search_context}

    Generate the itinerary now, following all rules.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=1200,
    )

    raw_output = response['choices'][0]['message']['content']
    return format_links(raw_output)

if st.button("Generate My Trip Ideas"):
    if destination:
        with st.spinner("Searching and building your itinerary..."):
            itinerary = generate_itinerary(destination, days)
            st.markdown(itinerary)
    else:
        st.warning("Please enter a destination.")

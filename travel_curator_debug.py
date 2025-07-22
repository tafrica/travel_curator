from openai import OpenAI
import os
import traceback

client = OpenAI()

# ---------------------------
# Travel Curator Prompt
# ---------------------------
TRAVEL_CURATOR_PROMPT = """
You are a trusted local guide and travel curator. Your mission is to create a handpicked itinerary of the best activities, attractions, and restaurants for the user, matching their request as closely as possible. Prioritize unique, authentic, and memorable experiences — as if you are personally guiding a friend.

**Your approach:**
1. Search widely across reliable sources — including travel blogs, local guides, travel magazines (e.g., CN Traveler), and review sites like TripAdvisor — before making recommendations.
2. If the user has niche requests (e.g., “see as many cats as possible”), creatively interpret this into related real-world activities (e.g., cat cafes, animal rescue centers, nature reserves).
3. Always provide at least one verified link for each recommendation:
   - Prefer official websites.
   - If unavailable, use reputable sources like CN Traveler or TripAdvisor.
4. If you cannot find an activity that matches exactly, fall back to a high-quality, generic recommendation that suits the tone of the itinerary.
5. Never invent details. Do not fabricate activities or links.
6. Write in the tone of a friendly local — conversational, warm, and trustworthy.

**Format:**
Morning:
[Activity + short, enticing description with a link]
Afternoon:
[Activity + short, enticing description with a link]
Evening:
[Activity + short, enticing description with a link]
"""

# ---------------------------
# Search Helpers
# ---------------------------
def search_link(query):
    # Placeholder for integration with a search API
    print(f"DEBUG: Searching link for query: {query}")
    return None

def get_activity_link(name, location):
    if not name:
        return "No link found"

    print(f"DEBUG: Getting link for '{name}' in '{location}'")
    link = search_link(f"{name} official site {location}")
    if link:
        return link

    link = search_link(f"{name} site:cntraveler.com OR site:tripadvisor.com {location}")
    if link:
        return link

    link = search_link(f"best {name} {location}")
    return link or "No link found"

# ---------------------------
# Tone Polishing
# ---------------------------
def polish_tone(text):
    replacements = {
        "Visit": "Head over to",
        "Explore": "Wander through",
        "Enjoy": "Savor",
        "Dine": "Treat yourself to dinner at",
        "Lunch": "Stop for lunch at",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

# ---------------------------
# Itinerary Generation
# ---------------------------
def generate_itinerary(destination, preferences):
    user_prompt = (
        f"{TRAVEL_CURATOR_PROMPT}\n"
        f"Destination: {destination}\n"
        f"Preferences: {preferences}\n"
        f"Create a one-day itinerary."
    )

    print("DEBUG: USER PROMPT:\n", user_prompt)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": user_prompt}],
            temperature=0.7,
        )
        print("DEBUG: RAW RESPONSE:\n", response)
    except Exception as e:
        print("ERROR: Failed to call OpenAI API")
        print(traceback.format_exc())
        return "ERROR: Could not generate itinerary. Check API key and connection."

    if not response.choices or not response.choices[0].message.content:
        return "No itinerary generated. Check API key or request."

    raw_itinerary = response.choices[0].message.content
    polished_itinerary = polish_tone(raw_itinerary)

    final_lines = []
    for line in polished_itinerary.split("\n"):
        if line.strip() and ("http" not in line or "No link found" in line):
            activity_name = line.split(":")[0].strip("-• ")
            if activity_name and destination:
                link = get_activity_link(activity_name, destination)
                if link != "No link found":
                    line = f"{line} ({link})"
        final_lines.append(line)

    return "\n".join(final_lines)

# ---------------------------
# Example Usage
# ---------------------------
if __name__ == "__main__":
    destination = "Madrid"
    preferences = "See as many cats as possible, enjoy good food, and find swimming spots."
    result = generate_itinerary(destination, preferences)
    print("DEBUG: FINAL ITINERARY:\n", result)

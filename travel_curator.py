from openai import OpenAI
import os

client = OpenAI()

def generate_itinerary(destination, preferences):
    user_prompt = f"""You are a travel curator. Create a 1-day itinerary for {destination} based on these preferences:
    {preferences}
    Format it as:
    Morning:
    [activity and short description]
    Afternoon:
    [activity and short description]
    Evening:
    [activity and short description]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": user_prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        # Fallback sample itinerary
        return f"""Morning:
- Explore {destination}'s local cafes and enjoy a relaxed breakfast.
Afternoon:
- Visit a popular market or cultural site.
Evening:
- Dine at a well-known restaurant and take a scenic walk.
(Note: Error fallback triggered: {e})
"""

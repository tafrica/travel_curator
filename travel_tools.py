import requests
from bs4 import BeautifulSoup

def get_tripadvisor_activities(destination):
    activities = []
    try:
        query = destination.replace(' ', '+')
        url = f"https://www.tripadvisor.com/Search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for activity links (common structure in TripAdvisor search results)
            for a in soup.select('a[href*="/Attraction_Review-"]', limit=5):
                name = a.get_text(strip=True)
                link = "https://www.tripadvisor.com" + a['href']
                activities.append(f"{name} ({link})")
    except Exception as e:
        activities.append(f"Error fetching TripAdvisor activities: {e}")
    return activities

def get_viator_activities(destination):
    activities = []
    try:
        query = destination.replace(' ', '+')
        url = f"https://www.viator.com/searchResults/all?text={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for activity links
            for a in soup.select('a[href*="/tours/"]', limit=5):
                name = a.get_text(strip=True)
                link = "https://www.viator.com" + a['href']
                activities.append(f"{name} ({link})")
    except Exception as e:
        activities.append(f"Error fetching Viator activities: {e}")
    return activities

def search_activities(destination):
    results = []
    # Try TripAdvisor
    results.extend(get_tripadvisor_activities(destination))
    # Try Viator
    results.extend(get_viator_activities(destination))
    # Fallback blog sources
    if not results:
        blog_sources = [
            f"Nomadic Matt search for {destination}: https://www.nomadicmatt.com/travel-blogs/?s={destination.replace(' ', '+')}",
            f"Conde Nast search for {destination}: https://www.cntraveler.com/search?q={destination.replace(' ', '+')}",
            f"TimeOut search for {destination}: https://www.timeout.com/search?query={destination.replace(' ', '+')}"
        ]
        results.extend(blog_sources)
    return results

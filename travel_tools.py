import requests

def search_activities(destination):
    """
    Search for activities using a priority of:
    1. Tripadvisor
    2. Viator
    3. Travel blogs, magazines, and event calendars
    Returns a list of strings with titles and URLs.
    """

    results = []

    # 1. Tripadvisor
    tripadvisor_url = f"https://www.tripadvisor.com/Search?q={destination.replace(' ', '+')}&searchSessionId="
    results.append(f"Tripadvisor search results for {destination}: {tripadvisor_url}")

    # 2. Viator
    viator_url = f"https://www.viator.com/searchResults/all?text={destination.replace(' ', '+')}"
    results.append(f"Viator search results for {destination}: {viator_url}")

    # 3. Travel blogs & magazines
    blog_sources = [
        f"https://www.nomadicmatt.com/travel-blogs/?s={destination.replace(' ', '+')}",
        f"https://www.cntraveler.com/search?q={destination.replace(' ', '+')}",
        f"https://www.timeout.com/search?query={destination.replace(' ', '+')}"
    ]
    for url in blog_sources:
        results.append(f"Blog/Magazine search: {url}")

    if not results:
        results.append("No data found.")

    return results

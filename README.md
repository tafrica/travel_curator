# Personalized Travel Curator

This is a Streamlit web app that generates a personalized travel itinerary based on your past trip preferences or dream vacation description.

## Features
- Enter a description of your ideal vacation or a past trip you loved.
- Specify a destination and number of days.
- Generate a unique day-by-day itinerary with activities and dining recommendations.

## Setup Instructions

### 1. Clone or Download This Repository
```bash
git clone https://github.com/your-username/travel-curator.git
cd travel-curator
```

### 2. Create a Virtual Environment (Optional but Recommended)
```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Add Your OpenAI API Key
Create a `.env` file in the project root with the following line:
```
OPENAI_API_KEY=sk-xxxxxx
```

### 5. Run Locally
```bash
streamlit run travel_curator.py
```

### 6. Deploy on Streamlit Cloud
- Push this code to a GitHub repository.
- Go to [Streamlit Cloud](https://streamlit.io/cloud) and select **Deploy from GitHub**.
- Add your `OPENAI_API_KEY` under the app's "Secrets" settings.

## Requirements
- Python 3.8+
- OpenAI API key (sign up at https://platform.openai.com/)

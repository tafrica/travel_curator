import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import date
import re
import urllib.parse
from io import BytesIO

import requests

def validate_links(text):
    pattern = r'\[(.*?)\]\((http[s]?://.*?)\)'
    matches = re.findall(pattern, text)
    for label, url in matches:
        try:
            r = requests.get(url, timeout=5, stream=True, allow_redirects=True)
            if r.status_code == 404:
                text = text.replace(f"({url})", "(No link found)")
        except:
            continue
    return text

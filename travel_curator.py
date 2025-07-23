import streamlit as st

st.write("DEBUG: Streamlit started successfully.")

try:
    st.set_page_config(page_title="Diagnostic Travel Curator", page_icon="🔍")
    st.write("DEBUG: Page config set.")
except Exception as e:
    st.error(f"Page config error: {e}")

st.title("🔍 Diagnostic Mode")
st.write("If you can see this, Streamlit is working.")

if st.button("Run Test"):
    st.write("DEBUG: Test button clicked.")

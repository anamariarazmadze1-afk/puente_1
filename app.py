"""Puente coordinator dashboard.

Entry point of the Streamlit app. Coordinators will review extracted
offers and needs on a map and approve proposed matches here.
"""

import streamlit as st

st.set_page_config(page_title="Puente", page_icon="🌉", layout="wide")

st.title("Puente")
st.subheader("Connecting people who need help with people who can help during a flood")

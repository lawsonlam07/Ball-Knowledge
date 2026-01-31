import streamlit as st
from events import TennisEvent
from prompts import generate_commentary, speak_text

st.set_page_config(page_title="CourtSide AI", layout="wide")

st.title("🎾 CourtSide AI | Live Commentary")

# Sidebar for Personas
st.sidebar.header("Commentator Settings")
persona = st.sidebar.select_slider(
    "Choose Personality",
    options=["Blind Aid", "Hype Man", "Professional Umpire"]
)

# Simulation for Testing (Since Team 2 isn't ready yet)
st.subheader("Manual Event Trigger (Internal Test)")
if st.button("Simulate Ace"):
    test_event = TennisEvent(event_type="Ace", player_name="Nadal", intensity=0.9)
    
    # 1. Get Text from Gemini
    commentary = generate_commentary(test_event, persona)
    st.write(f"**AI Commentator:** {commentary}")
    
    # 2. Get Audio from ElevenLabs
    # Note: In a real hackathon, you'd use a player library to stream the bytes
    st.audio(speak_text(commentary))
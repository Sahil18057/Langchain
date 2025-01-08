import streamlit as st
import cohere
from datetime import datetime

# Initialize Cohere client (replace with your API key)
COHERE_API_KEY = "o4SMHvCR9cSvNRtc2f8QtL6uEqXWfAo5mnNVF6Gn"
co = cohere.Client(COHERE_API_KEY)

def analyze_mood(text):
    """Analyze user mood using Cohere's generate endpoint."""
    try:
        response = co.generate(
            model="command-xlarge-nightly",
            prompt=f"""
Classify the mood of the following text into one of these categories:
Positive, Neutral, Negative, Stress, Anxiety, Depression.

Text: "{text}"
Mood:""",
            max_tokens=10,
            temperature=0,
            stop_sequences=["\n"]
        )
        sentiment = response.generations[0].text.strip()
        return sentiment
    except Exception as e:
        st.error("Cohere failed to respond: " + str(e))
        return "Default"

def get_personalized_activities(text, mood):
    """Provide tailored wellness activities using Cohere."""
    try:
        response = co.generate(
            model="command-xlarge-nightly",
            prompt=f"""
Based on the mood category '{mood}' detected from the following text, provide 2 tailored wellness activities that can help improve emotional health.

Text: "{text}"
Activities:""",
            max_tokens=100,
            temperature=0.7,
            stop_sequences=["\n"]
        )
        activities = response.generations[0].text.strip().split("\n")
        return activities if activities else None
    except Exception as e:
        st.warning("Cohere failed to provide tailored activities.")
        return None

def recommend_activities(mood):
    """Fallback wellness recommendations based on mood."""
    default_recommendations = {
        "Positive": [
            "Keep up the great mood! How about a gratitude journal entry?",
            "Celebrate by taking a nature walk!",
        ],
        "Neutral": [
            "Try a short meditation to center yourself.",
            "How about writing down three things you're grateful for?",
        ],
        "Negative": [
            "Take a deep breath and try a guided breathing exercise.",
            "Consider talking to a friend or family member about how you're feeling.",
        ],
        "Stress": [
            "Try progressive muscle relaxation to ease tension.",
            "Engage in a relaxing hobby like drawing or reading.",
        ],
        "Anxiety": [
            "Practice grounding techniques like the 5-4-3-2-1 exercise.",
            "Consider a yoga session to calm your mind and body.",
        ],
        "Depression": [
            "Reach out to a trusted friend or counselor.",
            "Start with small, manageable tasks to build momentum.",
        ],
    }
    return default_recommendations.get(mood, ["Explore some mindfulness activities!"])

def log_entry(mood, journal):
    """Log the user's mood and journal entry."""
    with open("mood_log.txt", "a") as file:
        file.write(f"{datetime.now()} | Mood: {mood} | Journal: {journal}\n")

def get_logged_entries():
    """Retrieve logged entries."""
    try:
        with open("mood_log.txt", "r") as file:
            return file.readlines()
    except FileNotFoundError:
        return []

# Streamlit UI
st.title("Mental Health Companion")

# Journaling and Mood Detection
st.header("Mood Detection")
journal_entry = st.text_area("How are you feeling today? Share your thoughts:")
if st.button("Analyze Mood"):
    if journal_entry.strip():
        mood = analyze_mood(journal_entry)
        if mood and mood != "Default":
            # Display mood in color
            mood_color = {
                "Positive": "green",
                "Neutral": "yellow",
                "Negative": "red",
                "Stress": "orange",
                "Anxiety": "blue",
                "Depression": "purple",
            }.get(mood, "gray")
            st.markdown(f"<p style='color:{mood_color}; font-size:20px;'>Detected Mood: {mood}</p>", unsafe_allow_html=True)

            # Cohere-tailored activities
            activities = get_personalized_activities(journal_entry, mood)
            if activities:
                st.write("**Tailored Recommendations:**")
                for activity in activities:
                    st.write(f"- {activity}")
            else:
                # Default activities as a fallback
                st.write("**Default Recommendations:**")
                default_activities = recommend_activities(mood)
                for activity in default_activities:
                    st.write(f"- {activity}")

            # Log the entry
            log_entry(mood, journal_entry)
        else:
            st.warning("Could not detect mood. Displaying default recommendations.")
            default_activities = recommend_activities("Neutral")
            for activity in default_activities:
                st.write(f"- {activity}")
    else:
        st.warning("Please enter some text to analyze.")

# Gamified Tracking
st.header("Gamified Tracking")
if st.button("Check Progress"):
    entries = get_logged_entries()
    if entries:
        st.write(f"**Total Entries:** {len(entries)}")
        st.write("Keep journaling to earn more badges!")
        for entry in entries[-5:]:  # Show the last 5 entries
            st.write(f"- {entry.strip()}")
    else:
        st.warning("No entries logged yet. Start journaling today!")

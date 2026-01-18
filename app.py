import streamlit as st
from src.core.planner import TravelPlanner
from dotenv import load_dotenv
import os
from elasticsearch import Elasticsearch
from datetime import datetime

# ---------------- UI SETUP ----------------
st.set_page_config(page_title="PlanMyTrip AI")
st.title("AI Trip Itinerary Planner")
st.write("Plan your day trip itinerary by entering your city and interests")

load_dotenv()

# ---------------- ELASTICSEARCH CLIENT ----------------
ELASTIC_URL = os.getenv("ELASTIC_URL")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")

es = Elasticsearch(
    ELASTIC_URL,
    api_key=ELASTIC_API_KEY
)

INDEX_NAME = "streamlit-logs"

# ---------------- FORM ----------------
with st.form("planner_form"):
    city = st.text_input("Enter the city name for your trip")
    interests = st.text_input("Enter your interests (comma-separated)")
    submitted = st.form_submit_button("Generate itinerary")

# ---------------- SUBMIT LOGIC ----------------
if submitted:
    if city and interests:
        try:
            # ---- Generate itinerary (NO streamlit inside planner) ----
            planner = TravelPlanner()
            planner.set_city(city)
            planner.set_interests(interests)
            itinerary = planner.create_itineary()

            # ---- Send to Elasticsearch FIRST ----
            doc = {
                "timestamp": datetime.utcnow(),
                "city": city,
                "interests": interests,
                "itinerary": itinerary,
                "app": "PlanMyTrip-AI",
                "environment": "kubernetes"
            }

            resp = es.index(index=INDEX_NAME, document=doc)

            # ---- UI OUTPUT AFTER LOGGING ----
            st.success(f"Saved to Elasticsearch ✔ (ID: {resp['_id']})")

            st.subheader("📄 Your Itinerary")
            st.markdown(itinerary)

        except Exception as e:
            st.error("❌ Something went wrong")
            st.exception(e)

    else:
        st.warning("Please fill City and Interests")

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
    st.write("STEP 1: Submitted")

    if city and interests:
        try:
            st.write("STEP 2: Creating planner")

            planner = TravelPlanner()
            planner.set_city(city)
            planner.set_interests(interests)

            st.write("STEP 3: Calling LLM")
            itinerary = planner.create_itineary()

            st.write("STEP 4: LLM returned")

            doc = {
                "timestamp": datetime.utcnow(),
                "city": city,
                "interests": interests,
                "itinerary": itinerary,
                "app": "PlanMyTrip-AI",
                "environment": "kubernetes"
            }

            st.write("STEP 5: Sending to Elasticsearch")

            resp = es.index(index=INDEX_NAME, document=doc)

            st.write("STEP 6: Elasticsearch response received")
            st.success(f"Saved ✔ ID: {resp['_id']}")

            st.subheader("📄 Your Itinerary")
            st.markdown(itinerary)

        except Exception as e:
            st.error("❌ ERROR OCCURRED")
            st.exception(e)
    else:
        st.warning("Please fill City and Interests")

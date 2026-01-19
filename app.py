import streamlit as st
from src.core.planner import TravelPlanner
from dotenv import load_dotenv
import os
from elasticsearch import Elasticsearch
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="PlanMyTrip AI")
st.title("AI Trip Itinerary Planner")
st.write("Plan your day trip itinerary by entering your city and interests")

load_dotenv()

# ---------------- ES CLIENT ----------------
es = Elasticsearch(
    os.getenv("ELASTIC_URL"),
    api_key=os.getenv("ELASTIC_API_KEY"),
    request_timeout=30
)

INDEX_NAME = "streamlit-logs"

# ---------------- SESSION STATE ----------------
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# ---------------- FORM ----------------
with st.form("planner_form"):
    city = st.text_input("Enter the city name for your trip")
    interests = st.text_input("Enter your interests (comma-separated)")
    submit_btn = st.form_submit_button("Generate itinerary")

    if submit_btn:
        st.session_state.submitted = True

# ---------------- PROCESS ----------------
if st.session_state.submitted:

    if city and interests:
        try:
            planner = TravelPlanner()
            planner.set_city(city)
            planner.set_interests(interests)
            itinerary = planner.create_itineary()

            st.subheader("📄 Your Itinerary")
            st.markdown(itinerary)

            # -------- SAVE TO ELASTICSEARCH --------
            doc = {
                "timestamp": datetime.utcnow().isoformat(),
                "city": city,
                "interests": interests,
                "itinerary": itinerary,
                "itinerary_length": len(itinerary),
                "app": "PlanMyTrip-AI",
                "environment": "kubernetes"
            }

            resp = es.index(
                index=INDEX_NAME,
                document=doc,
                refresh="wait_for"
            )

            if resp.get("result") in ["created", "updated"]:
                st.success("✅ Saved to Elasticsearch")
            else:
                st.warning("⚠ Saved but unexpected ES response")

        except Exception as e:
            st.error("❌ Failed to save to Elasticsearch")
            st.exception(e)

    else:
        st.warning("Please fill City and Interests")

    # prevent resubmission on rerun
    st.session_state.submitted = False
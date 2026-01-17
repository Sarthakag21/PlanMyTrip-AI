import streamlit as st
from src.core.planner import TravelPlanner
from dotenv import load_dotenv

# ✅ Elastic logging imports
from elasticsearch import Elasticsearch
import os
from datetime import datetime

# ------------------ BASIC APP SETUP ------------------

st.set_page_config(page_title="PlanMyTrip AI")
st.title("AI Trip Itinerary Planner")
st.write("Plan your day trip itinerary by entering your city and interests")

load_dotenv()

# ------------------ ELASTIC CLOUD LOGGING SETUP ------------------

ES_URL = os.getenv("ELASTIC_URL")
ES_API_KEY = os.getenv("ELASTIC_API_KEY")

es = Elasticsearch(
    ES_URL,
    api_key=ES_API_KEY,
    verify_certs=True
)

def send_log(level, message, extra=None):
    doc = {
        "@timestamp": datetime.utcnow(),
        "level": level,
        "message": message,
        "service": "streamlit-app",
        "environment": "kubernetes"
    }
    if extra:
        doc.update(extra)

    es.index(index="streamlit-logs", document=doc)

# ✅ Log when app starts
send_log("INFO", "Streamlit app started successfully")

# ------------------ UI FORM ------------------

with st.form("planner_form"):
    city = st.text_input("Enter the city name for your trip")
    interests = st.text_input("Enter your interests (comma-separated)")
    submitted = st.form_submit_button("Generate itinerary")

    if submitted:
        send_log("INFO", "Form submitted", {
            "city": city,
            "interests": interests
        })

        if city and interests:
            try:
                planner = TravelPlanner()
                planner.set_city(city)
                planner.set_interests(interests)

                send_log("INFO", "Generating itinerary")

                itinerary = planner.create_itineary()

                send_log("INFO", "Itinerary generated successfully")

                st.subheader("📄 Your Itinerary")
                st.markdown(itinerary)

            except Exception as e:
                send_log("ERROR", "Itinerary generation failed", {
                    "error": str(e)
                })
                st.error("Something went wrong while generating itinerary.")

        else:
            send_log("WARNING", "Form submitted with missing fields")
            st.warning("Please fill City and Interests to move forward.")
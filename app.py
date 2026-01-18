import streamlit as st
from src.core.planner import TravelPlanner
from dotenv import load_dotenv
import os
from elasticsearch import Elasticsearch
from datetime import datetime

st.set_page_config(page_title="PlanMyTrip AI")
st.title("AI Trip Itinerary Planner")
st.write("Plan your day trip itinerary by entering your city and interests")

load_dotenv()

# ---- Elasticsearch Client ----
es = Elasticsearch(
    os.getenv("ELASTIC_URL"),
    api_key=os.getenv("ELASTIC_API_KEY")
)

INDEX_NAME = "streamlit-logs"

with st.form("planner_form"):
    city = st.text_input("Enter the city name for your trip")
    interests = st.text_input("Enter your interests (comma-separated)")
    submitted = st.form_submit_button("Generate itinerary")

    if submitted:
        if city and interests:
            planner = TravelPlanner()
            planner.set_city(city)
            planner.set_interests(interests)
            itinerary = planner.create_itineary()

            st.subheader("📄 Your Itinerary")
            st.markdown(itinerary)

            # ---- Send to Elasticsearch ----
            doc = {
                "timestamp": datetime.utcnow(),
                "city": city,
                "interests": interests,
                "itinerary": itinerary,
                "app": "PlanMyTrip-AI",
                "environment": "kubernetes"
            }

            es.index(index=INDEX_NAME, document=doc)

            st.success("Saved to Elasticsearch ✔")

        else:
            st.warning("Please fill City and Interests")
import os
import streamlit as st
import google.generativeai as genai
from amadeus import Client
from dotenv import load_dotenv
load_dotenv()
def load_api_keys():
    '''Load API keys from environment variables'''
    return {
        'gemini': os.getenv('GEMINI_API_KEY', ''),
        'amadeus_key': os.getenv('AMADEUS_API_KEY', ''),
        'amadeus_secret': os.getenv('AMADEUS_API_SECRET', ''),
        'weather': os.getenv('OPENWEATHER_API_KEY', '')
    }

def initialize_apis():
    '''Initialize all API clients from environment variables'''
    keys = load_api_keys()
    apis = {'gemini': None, 'amadeus': None, 'weather_key': None}
    
    return apis
# Streamlit page configuration
def setup_page():
    st.set_page_config(
        page_title="Smart AI Travel Planner",
        layout="wide",
        page_icon="✈️"
    )
    
    # Custom CSS
    st.markdown('''
        <style>
        .big-font {font-size:20px !important; font-weight: bold;}
        .metric-card {background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 10px 0;}
        </style>
    ''', unsafe_allow_html=True)
import streamlit as st
from config import setup_page, initialize_apis
from ui_components import (render_input_form, render_summary_cards,
    render_insights, render_flights, render_hotels, render_itinerary
)
from visualizations import render_budget_visualizations, render_weather_charts
from utils import validate_form_data, render_export_section
from agent import TravelAgent

def main():
    # Setup page configuration
    setup_page()
    
    # Title
    st.title("✈️ Smart AI Travel Planner")
    st.markdown("### 🤖 Powered by Agentic AI: Perceive → Reason → Plan → Act")
    st.markdown("---")
    
    # Initialize APIs and render sidebar
    
    apis = initialize_apis()
    
    # Render input form
    form_data = render_input_form()
    
    # Process form submission
    if form_data['submitted']:
        if not validate_form_data(form_data):
            return
        
        # Initialize AI Agent
        agent = TravelAgent(form_data, apis)
        
        # Execute Agentic AI Workflow with progress tracking
        st.markdown("---")
        st.header("🤖 AI Agent Working...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("Processing your travel plan..."):
            # PERCEIVE
            status_text.text("🔍 Perceiving: Gathering data...")
            progress_bar.progress(25)
            agent.perceive()
            
            # REASON
            status_text.text("🧠 Reasoning: Analyzing options...")
            progress_bar.progress(50)
            agent.reason()
            
            # PLAN
            status_text.text("📋 Planning: Creating itinerary...")
            progress_bar.progress(75)
            agent.plan()
            
            # ACT
            status_text.text("🚀 Acting: Compiling results...")
            progress_bar.progress(100)
            result = agent.act()
        
        status_text.empty()
        progress_bar.empty()
        
        # Display Results
        st.success("🎉 Your Personalized Travel Plan is Ready!")
        st.markdown("---")
        
        # AI Reasoning Summary
        with st.expander("🧠 AI Reasoning & Analysis", expanded=False):
            st.markdown(result['reasoning'])
        
        # Summary Cards
        render_summary_cards(result)
        
        # Budget Visualizations
        render_budget_visualizations(result)
        
        # Key Insights
        render_insights(result['insights'])
        
        # Flight Options
        render_flights(result)
        
        # Hotel Options
        render_hotels(result)
        
        # Day-by-Day Itinerary
        render_itinerary(result)
        
        # Weather Forecast
        render_weather_charts(result, result['insights'])
        
        # Export Options
        render_export_section(result, form_data['destination'], form_data['start_date'])
        
        st.success("✨ **Thank you for using Smart AI Travel Planner!** Have an amazing trip! 🌍✈️")

if __name__ == "__main__":
    main()
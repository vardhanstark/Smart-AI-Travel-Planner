import json
import streamlit as st

def validate_form_data(form_data):
    '''Validate form submission'''
    if not form_data['destination'] or not form_data['origin']:
        st.error("⚠️ Please fill in destination and origin cities!")
        return False
    
    if not form_data['interests']:
        st.error("⚠️ Please select at least one interest!")
        return False
    
    from datetime import datetime
    start = datetime.strptime(form_data['start_date'], '%Y-%m-%d')
    end = datetime.strptime(form_data['end_date'], '%Y-%m-%d')
    
    if end <= start:
        st.error("⚠️ End date must be after start date!")
        return False
    
    return True

def generate_export_data(result, destination, start_date):
    '''Generate export files'''
    
    # JSON Export
    json_data = json.dumps(result, indent=2, default=str)
    
    # Text Summary
    text_summary = f"""
SMART AI TRAVEL PLANNER
========================

Destination: {result['summary']['destination']}
Duration: {result['summary']['duration']} days
Budget: ${result['summary']['total_budget']}
Dates: {result['summary']['dates']}

BUDGET BREAKDOWN:
{chr(10).join([f"- {k.title()}: ${v}" for k, v in result['budget_breakdown'].items()])}

SELECTED FLIGHT:
Price: ${result['flight']['price']['total'] if result['flight'] else 'N/A'}

SELECTED HOTEL:
{result['hotel']['hotel']['name'] if result['hotel'] else 'N/A'}
Price: ${result['hotel']['offers'][0]['price']['total'] if result['hotel'] else 'N/A'}

DAY-BY-DAY ITINERARY:
{chr(10).join([f"Day {d['day_number']}: {d['date']}\n  Morning: {d['morning']['activity']}\n  Afternoon: {d['afternoon']['activity']}\n  Evening: {d['evening']['activity']}\n" for d in result['itinerary'].values()])}
"""
    
    return json_data, text_summary

def render_export_section(result, destination, start_date):
    '''Render export options'''
    st.header("📥 Export Your Travel Plan")
    
    json_data, text_summary = generate_export_data(result, destination, start_date)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="📄 Download as JSON",
            data=json_data,
            file_name=f"travel_plan_{destination.replace(' ', '_')}_{start_date.replace('-', '')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        st.download_button(
            label="📝 Download as Text",
            data=text_summary,
            file_name=f"travel_plan_{destination.replace(' ', '_')}_{start_date.replace('-', '')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col3:
        st.info("📧 **Email Option**\n\nCopy text and email to yourself!")
    
    st.markdown("---")
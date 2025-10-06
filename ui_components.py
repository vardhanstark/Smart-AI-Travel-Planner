import streamlit as st
from datetime import datetime, timedelta
def render_input_form():
    '''Render the main input form'''
    st.header("📝 Plan Your Perfect Trip")
    
    with st.form("travel_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            destination = st.text_input("🌍 Destination City*", placeholder="e.g., Paris, Tokyo")
            start_date = st.date_input("📅 Start Date*", min_value=datetime.today(), value=datetime.today())
            budget = st.number_input("💰 Total Budget (USD)*", min_value=500, max_value=50000, step=100, value=2000)
        
        with col2:
            origin = st.text_input("🏠 Departure City*", placeholder="e.g., London, Mumbai")
            end_date = st.date_input("📅 End Date*", min_value=datetime.today() + timedelta(days=1), value=datetime.today() + timedelta(days=5))
            travel_style = st.selectbox("🎨 Travel Style*", ["budget", "mid-range", "luxury"])
        
        with col3:
            pace = st.radio("⚡ Travel Pace*", ["relaxed", "moderate", "intensive"], horizontal=False)
        
        st.markdown("---")
        
        interests = st.multiselect(
            "🎯 Your Interests* (Select multiple)",
            ["Culture & Art", "Food & Gastronomy", "Adventure & Outdoor", 
             "History & Heritage", "Shopping", "Nature & Wildlife", "Relaxation"],
            help="Select activities you enjoy"
        )
        
        st.markdown("---")
        submitted = st.form_submit_button("🚀 Generate My Travel Plan", type="primary", use_container_width=True)
    
    if submitted:
        return {
            'submitted': True,
            'destination': destination,
            'origin': origin,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'budget': budget,
            'interests': interests,
            'travel_style': travel_style,
            'pace': pace
        }
    
    return {'submitted': False}

def render_summary_cards(result):
    '''Render trip overview cards'''
    st.header("📊 Trip Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🌍 Destination", result['summary']['destination'])
    with col2:
        st.metric("📅 Duration", f"{result['summary']['duration']} days")
    with col3:
        st.metric("💰 Total Budget", f"${result['summary']['total_budget']}")
    with col4:
        st.metric("✈️ Travel Style", result['summary']['travel_style'].title())
    
    st.markdown("---")

def render_insights(insights):
    '''Render key insights section'''
    st.header("💡 Key Insights & Recommendations")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**💰 Cost Optimization**\n\n{insights['cost_savings']}")
    with col2:
        st.success(f"**📊 Budget Usage**\n\n{insights['budget_utilization']} utilized")
    with col3:
        st.warning(f"**📈 Daily Average**\n\n{insights['daily_average']} per day")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🎯 Smart Recommendations")
        for rec in insights['recommendations']:
            st.write(f"✓ {rec}")
    
    with col2:
        st.markdown("#### 💵 Money-Saving Tips")
        for tip in insights['money_saving_tips']:
            st.write(f"💰 {tip}")
    
    st.markdown("---")

def render_flights(result):
    '''Render flight options'''
    st.header("✈️ Flight Options")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🌟 Selected Flight (Best Value)")
        if result['flight']:
            flight = result['flight']
            segment = flight['itineraries'][0]['segments'][0]
            
            flight_col1, flight_col2, flight_col3 = st.columns(3)
            with flight_col1:
                st.write(f"**Airline:** {flight.get('validatingAirlineCodes', ['N/A'])[0]}")
                st.write(f"**Flight:** {segment.get('carrierCode', 'XX')}-{segment.get('number', '0000')}")
            with flight_col2:
                st.write(f"**Departure:** {segment['departure']['at']}")
                st.write(f"**Arrival:** {segment['arrival']['at']}")
            with flight_col3:
                st.write(f"**Duration:** {flight['itineraries'][0]['duration']}")
                st.write(f"**Price:** ${flight['price']['total']}")
    
    with col2:
        st.subheader("Alternative Options")
        alt_flights = result['all_flights'][1:4]
        for i, alt in enumerate(alt_flights, 1):
            st.caption(f"Option {i+1}: ${alt['price']['total']}")
    
    st.markdown("---")

def render_hotels(result):
    '''Render hotel options'''
    st.header("🏨 Accommodation Options")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🌟 Selected Hotel (Best Match)")
        if result['hotel']:
            hotel = result['hotel']
            offer = hotel['offers'][0]
            
            hotel_col1, hotel_col2 = st.columns(2)
            with hotel_col1:
                st.write(f"**Hotel:** {hotel['hotel']['name']}")
                st.write(f"**Rating:** {'⭐' * hotel['hotel'].get('rating', 4)}")
                st.write(f"**Room Type:** {offer['room']['description']['text']}")
            with hotel_col2:
                st.write(f"**Price/Night:** ${offer['price']['base']}")
                st.write(f"**Total Cost:** ${offer['price']['total']}")
                st.write(f"**Amenities:** {', '.join(hotel.get('amenities', ['WiFi', 'Breakfast'])[:3])}")
    
    with col2:
        st.subheader("Alternative Hotels")
        alt_hotels = result['all_hotels'][1:4]
        for i, alt in enumerate(alt_hotels, 1):
            st.caption(f"{alt['hotel']['name']}: ${alt['offers'][0]['price']['base']}/night")
    
    st.markdown("---")

def render_itinerary(result):
    '''Render day-by-day itinerary'''
    st.header("📅 Detailed Day-by-Day Itinerary")
    
    for day_key, day_data in result['itinerary'].items():
        with st.expander(
            f"**Day {day_data['day_number']}: {day_data['date']}** | "
            f"☁️ {day_data['weather']['condition']} ({day_data['weather']['temperature']}) | "
            f"💵 ${day_data['total_cost']} | "
            f"⚡ {day_data['energy_level']} Pace",
            expanded=(day_data['day_number'] == 1)
        ):
            st.info(f"🌤️ {day_data['weather']['recommendation']}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 🌅 Morning")
                st.write(f"**⏰ {day_data['morning']['time']}**")
                st.write(f"**📍 {day_data['morning']['activity']}**")
                st.write(f"⭐ Rating: {day_data['morning']['rating']}/5.0")
                st.write(f"💵 Cost: ${day_data['morning']['cost']}")
                st.caption(day_data['morning']['description'])
            
            with col2:
                st.markdown("### ☀️ Afternoon")
                st.write(f"**⏰ {day_data['afternoon']['time']}**")
                st.write(f"**📍 {day_data['afternoon']['activity']}**")
                st.write(f"⭐ Rating: {day_data['afternoon']['rating']}/5.0")
                st.write(f"💵 Cost: ${day_data['afternoon']['cost']}")
                st.caption(day_data['afternoon']['description'])
            
            with col3:
                st.markdown("### 🌙 Evening")
                st.write(f"**⏰ {day_data['evening']['time']}**")
                st.write(f"**📍 {day_data['evening']['activity']}**")
                st.write(f"⭐ Rating: {day_data['evening']['rating']}/5.0")
                st.write(f"💵 Cost: ${day_data['evening']['cost']}")
                st.caption(day_data['evening']['description'])
            
            st.markdown("---")
            st.success(f"💡 **Daily Tips:** {day_data['tips']}")
    
    st.markdown("---")
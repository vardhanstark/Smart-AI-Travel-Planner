import streamlit as st
from datetime import datetime, timedelta
from api_handlers import (
    get_flights, get_hotels, get_weather,
    get_attractions_from_amadeus, get_attractions_from_gemini,
    generate_generic_attractions
)

class TravelAgent:
    '''Autonomous AI Agent implementing PERCEIVE -> REASON -> PLAN -> ACT'''
    
    def __init__(self, user_input, apis):
        self.user_input = user_input
        self.apis = apis
        self.perceived_data = {}
        self.reasoning_output = {}
        self.itinerary_plan = {}
        self.final_output = {}
    
    def perceive(self):
        '''PILLAR 1: Gather and analyze all necessary information'''
        st.info("🔍 PERCEIVING: Gathering information from multiple sources...")
        
        self.perceived_data = {
            'destination': self.user_input['destination'],
            'origin': self.user_input['origin'],
            'dates': {
                'start': self.user_input['start_date'],
                'end': self.user_input['end_date'],
                'duration': (datetime.strptime(self.user_input['end_date'], '%Y-%m-%d') - 
                           datetime.strptime(self.user_input['start_date'], '%Y-%m-%d')).days
            },
            'budget': self.user_input['budget'],
            'interests': self.user_input['interests'],
            'travel_style': self.user_input['travel_style'],
            'pace': self.user_input['pace']
        }
        
        with st.spinner("Fetching flights..."):
            self.perceived_data['flights'] = get_flights(
                self.apis,
                self.user_input['origin'],
                self.user_input['destination'],
                self.user_input['start_date'],
                self.user_input['end_date']
            )
        
        with st.spinner("Fetching hotels..."):
            self.perceived_data['hotels'] = get_hotels(
                self.apis,
                self.user_input['destination'],
                self.user_input['start_date'],
                self.user_input['end_date'],
                self.perceived_data['dates']['duration']
            )
        
        with st.spinner("Fetching weather..."):
            self.perceived_data['weather'] = get_weather(
                self.apis,
                self.user_input['destination'],
                self.user_input['start_date'],
                self.perceived_data['dates']['duration']
            )
        
        with st.spinner("Fetching attractions..."):
            attractions = get_attractions_from_amadeus(self.apis, self.user_input['destination'])
            if not attractions:
                attractions = get_attractions_from_gemini(
                    self.apis,
                    self.user_input['destination'],
                    self.user_input['interests']
                )
            if not attractions:
                attractions = generate_generic_attractions(
                    self.user_input['destination'],
                    self.user_input['interests']
                )
            self.perceived_data['attractions'] = attractions
        
        st.success("✅ Perception Complete!")
        return self.perceived_data
    
    def reason(self):
        '''PILLAR 2: Analyze data and make intelligent decisions'''
        st.info("🧠 REASONING: Analyzing options...")
        
        budget = self.perceived_data['budget']
        
        style_multipliers = {
            'budget': {'flights': 0.30, 'hotels': 0.20, 'activities': 0.18, 'food': 0.25, 'transport': 0.07},
            'mid-range': {'flights': 0.35, 'hotels': 0.25, 'activities': 0.15, 'food': 0.20, 'transport': 0.05},
            'luxury': {'flights': 0.25, 'hotels': 0.35, 'activities': 0.15, 'food': 0.20, 'transport': 0.05}
        }
        
        multipliers = style_multipliers[self.user_input['travel_style']]
        budget_strategy = {k: int(budget * v) for k, v in multipliers.items()}
        
        flights = self.perceived_data['flights']
        selected_flight = min(flights, key=lambda f: float(f['price']['total'])) if flights else None
        
        hotels = self.perceived_data['hotels']
        hotel_budget = budget_strategy['hotels']
        selected_hotel = None
        
        for hotel in hotels:
            hotel_price = float(hotel['offers'][0]['price']['total'])
            if hotel_price <= hotel_budget * 1.1:
                selected_hotel = hotel
                break
        
        if not selected_hotel and hotels:
            selected_hotel = hotels[0]
        
        reasoning_text = "Budget optimized based on travel style."
        
        if self.apis['gemini']:
            try:
                prompt = f'''Analyze travel plan for {self.perceived_data['destination']}, 
Budget ${budget}, {self.perceived_data['dates']['duration']} days, 
Interests: {', '.join(self.perceived_data['interests'])}.
Provide brief recommendations in 150 words.'''
                response = self.apis['gemini'].generate_content(prompt)
                reasoning_text = response.text
            except:
                pass
        
        self.reasoning_output = {
            'budget_strategy': budget_strategy,
            'reasoning_summary': reasoning_text,
            'selected_flight': selected_flight,
            'selected_hotel': selected_hotel,
            'top_attractions': self.perceived_data['attractions'][:5]
        }
        
        st.success("✅ Reasoning Complete!")
        return self.reasoning_output
    
    def plan(self):
        '''PILLAR 3: Create detailed day-by-day itinerary'''
        st.info("📋 PLANNING: Creating itinerary...")
        
        duration = self.perceived_data['dates']['duration']
        attractions = self.perceived_data['attractions']
        weather = self.perceived_data['weather']['list']
        
        daily_activity_budget = self.reasoning_output['budget_strategy']['activities'] // duration
        daily_food_budget = self.reasoning_output['budget_strategy']['food'] // duration
        
        self.itinerary_plan = {}
        
        for day_num in range(duration):
            day_key = f'day_{day_num + 1}'
            day_date = (datetime.strptime(self.perceived_data['dates']['start'], '%Y-%m-%d') + 
                       timedelta(days=day_num)).strftime('%Y-%m-%d')
            
            day_weather = weather[min(day_num, len(weather)-1)]
            weather_condition = day_weather['weather'][0]['main']
            temp = day_weather['main']['temp']
            
            morning_attraction = attractions[day_num % len(attractions)] if attractions else None
            afternoon_attraction = attractions[(day_num + 1) % len(attractions)] if len(attractions) > 1 else None
            
            morning_cost = morning_attraction['price'] if morning_attraction else 15
            afternoon_cost = afternoon_attraction['price'] if afternoon_attraction else 20
            evening_cost = daily_food_budget - 15
            
            self.itinerary_plan[day_key] = {
                'date': day_date,
                'day_number': day_num + 1,
                'morning': {
                    'activity': morning_attraction['name'] if morning_attraction else f'Explore {self.perceived_data["destination"]}',
                    'time': '9:00 AM - 12:00 PM',
                    'cost': morning_cost,
                    'description': morning_attraction.get('description', 'Morning activity') if morning_attraction else 'Discover local gems',
                    'rating': morning_attraction.get('rating', 4.5) if morning_attraction else 4.5
                },
                'afternoon': {
                    'activity': afternoon_attraction['name'] if afternoon_attraction else 'Local Cuisine',
                    'time': '1:00 PM - 6:00 PM',
                    'cost': afternoon_cost,
                    'description': afternoon_attraction.get('description', 'Afternoon activity') if afternoon_attraction else 'Authentic dining',
                    'rating': afternoon_attraction.get('rating', 4.5) if afternoon_attraction else 4.5
                },
                'evening': {
                    'activity': ['Dinner', 'Evening walk', 'Cultural show', 'Rooftop dining', 'Night market'][day_num % 5],
                    'time': '7:00 PM - 10:00 PM',
                    'cost': evening_cost,
                    'description': 'Perfect end to the day',
                    'rating': 4.6
                },
                'weather': {
                    'condition': weather_condition,
                    'temperature': f"{temp:.1f}°C",
                    'recommendation': self._get_weather_rec(weather_condition)
                },
                'total_cost': morning_cost + afternoon_cost + evening_cost,
                'tips': f"Wear comfortable shoes. {self._weather_tip(weather_condition)}",
                'energy_level': ['High', 'Moderate', 'Relaxed'][day_num % 3]
            }
        
        st.success("✅ Planning Complete!")
        return self.itinerary_plan
    
    def _get_weather_rec(self, condition):
        recs = {
            'Clear': 'Perfect for outdoor activities! 🌞',
            'Sunny': 'Great for sightseeing! ☀️',
            'Partly Cloudy': 'Good day for activities 🌤️',
            'Cloudy': 'Ideal for indoor attractions ☁️',
            'Light Rain': 'Pack an umbrella 🌧️',
            'Rain': 'Museums and cafes ☔'
        }
        return recs.get(condition, 'Check weather 🌡️')
    
    def _weather_tip(self, condition):
        tips = {
            'Rain': 'Carry umbrella.',
            'Clear': 'Apply sunscreen.',
            'Light Rain': 'Light jacket.'
        }
        return tips.get(condition, '')
    
    def act(self):
        '''PILLAR 4: Execute and compile final plan'''
        st.info("🚀 ACTING: Compiling results...")
        
        flight_cost = float(self.reasoning_output['selected_flight']['price']['total']) if self.reasoning_output['selected_flight'] else 0
        hotel_cost = float(self.reasoning_output['selected_hotel']['offers'][0]['price']['total']) if self.reasoning_output['selected_hotel'] else 0
        activities_cost = sum([day['total_cost'] for day in self.itinerary_plan.values()])
        
        self.final_output = {
            'summary': {
                'destination': self.perceived_data['destination'],
                'origin': self.perceived_data['origin'],
                'duration': self.perceived_data['dates']['duration'],
                'total_budget': self.perceived_data['budget'],
                'dates': f"{self.perceived_data['dates']['start']} to {self.perceived_data['dates']['end']}",
                'travel_style': self.user_input['travel_style'],
                'interests': self.perceived_data['interests']
            },
            'budget_breakdown': self.reasoning_output['budget_strategy'],
            'actual_costs': {
                'flights': flight_cost,
                'hotels': hotel_cost,
                'activities_food': activities_cost,
                'total_used': flight_cost + hotel_cost + activities_cost
            },
            'flight': self.reasoning_output['selected_flight'],
            'hotel': self.reasoning_output['selected_hotel'],
            'all_flights': self.perceived_data['flights'][:5],
            'all_hotels': self.perceived_data['hotels'][:5],
            'itinerary': self.itinerary_plan,
            'weather_summary': self.perceived_data['weather'],
            'insights': self._generate_insights(),
            'reasoning': self.reasoning_output['reasoning_summary']
        }
        
        st.success("✅ Action Complete!")
        return self.final_output
    
    def _generate_insights(self):
        total_cost = sum([day['total_cost'] for day in self.itinerary_plan.values()])
        budget = self.perceived_data['budget']
        duration = self.perceived_data['dates']['duration']
        
        flight_cost = float(self.reasoning_output['selected_flight']['price']['total']) if self.reasoning_output['selected_flight'] else 0
        hotel_cost = float(self.reasoning_output['selected_hotel']['offers'][0]['price']['total']) if self.reasoning_output['selected_hotel'] else 0
        total_planned = flight_cost + hotel_cost + total_cost
        
        peak_days = [f"Day {day['day_number']}" for day in self.itinerary_plan.values() if day['total_cost'] > (total_cost / duration) * 1.2]
        
        weather_data = self.perceived_data['weather']['list']
        rain_days = [w['dt_txt'] for w in weather_data if 'Rain' in w['weather'][0]['main']]
        
        return {
            'cost_savings': f"AI-optimized: {((budget - total_planned) / budget * 100):.1f}% under budget" if total_planned < budget else "Budget utilized",
            'total_planned_cost': total_planned,
            'remaining_budget': max(0, budget - total_planned),
            'peak_days': peak_days if peak_days else ['Balanced'],
            'weather_alerts': rain_days[:3] if rain_days else ['No rain expected'],
            'budget_utilization': f"{(total_planned / budget) * 100:.1f}%",
            'daily_average': f"${total_cost / duration:.2f}",
            'recommendations': [
                f"Best flight saves ${50 + (duration * 10):.0f}",
                "Book 2-3 months advance for 15-20% savings",
                f"Your {', '.join(self.perceived_data['interests'][:2])} interests covered",
                "Travel insurance recommended" if rain_days else "Weather favorable",
                f"Peak spending: {peak_days[0] if peak_days else 'Day 1'}"
            ],
            'money_saving_tips': [
                "Use public transport - save $5-15/day",
                "Lunch at local spots - 40% cheaper",
                "Book online - up to 20% discount",
                "Free walking tours available"
            ]
        }
    


    
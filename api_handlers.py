import requests
import streamlit as st
from datetime import datetime, timedelta
import json

def get_flights(apis, origin, destination, start_date, end_date):
    '''Fetch flight data from Amadeus API or simulate'''
    if apis['amadeus']:
        try:
            response = apis['amadeus'].shopping.flight_offers_search.get(
                originLocationCode=origin[:3].upper(),
                destinationLocationCode=destination[:3].upper(),
                departureDate=start_date,
                returnDate=end_date,
                adults=1,
                max=5
            )
            return response.data
        except Exception as e:
            st.warning(f"Using simulated flight data: {str(e)}")
    
    # Simulated flight data
    return [
        {
            'id': f'FLIGHT_{i}',
            'price': {'total': str(300 + i*75), 'currency': 'USD'},
            'itineraries': [{
                'duration': f'PT{5+i}H{30+(i*10)}M',
                'segments': [{
                    'departure': {
                        'iataCode': origin[:3].upper(),
                        'at': f'{start_date}T{8+i}:00:00'
                    },
                    'arrival': {
                        'iataCode': destination[:3].upper(),
                        'at': f'{start_date}T{14+i}:30:00'
                    },
                    'carrierCode': ['AA', 'DL', 'UA', 'BA', 'LH'][i],
                    'number': f'{1000+i*100}',
                    'aircraft': {'code': '32A'}
                }]
            }],
            'validatingAirlineCodes': [['American', 'Delta', 'United', 'British Airways', 'Lufthansa'][i]]
        } for i in range(5)
    ]

def get_hotels(apis, destination, start_date, end_date, duration):
    '''Fetch hotel data from Amadeus API or simulate'''
    if apis['amadeus']:
        try:
            city_response = apis['amadeus'].reference_data.locations.get(
                keyword=destination,
                subType='CITY'
            )
            if city_response.data:
                city_code = city_response.data[0]['iataCode']
                hotel_response = apis['amadeus'].shopping.hotel_offers.get(
                    cityCode=city_code,
                    checkInDate=start_date,
                    checkOutDate=end_date,
                    adults=1
                )
                return hotel_response.data[:5]
        except Exception as e:
            st.warning(f"Using simulated hotel data: {str(e)}")
    
    # Simulated hotel data
    hotel_types = ['Budget Inn', 'Comfort Hotel', 'Grand Plaza', 'Premium Suites', 'Elite Resort']
    room_types = ['Standard Room', 'Deluxe Room', 'Superior Room', 'Executive Suite', 'Luxury Suite']
    
    return [
        {
            'hotel': {
                'name': f'{hotel_types[i]} {destination}',
                'rating': 3 + i,
                'cityCode': destination[:3].upper()
            },
            'offers': [{
                'id': f'HOTEL_{i}',
                'checkInDate': start_date,
                'checkOutDate': end_date,
                'price': {
                    'total': str((80 + i*40) * duration),
                    'currency': 'USD',
                    'base': str(80 + i*40)
                },
                'room': {
                    'type': 'STANDARD',
                    'description': {'text': room_types[i]}
                },
                'guests': {'adults': 1}
            }],
            'amenities': ['WiFi', 'Breakfast', 'Pool', 'Gym', 'Spa'][:i+2]
        } for i in range(5)
    ]

def get_weather(apis, destination, start_date, duration):
    '''Fetch weather data from OpenWeather API or simulate'''
    if apis['weather_key']:
        try:
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={destination}&appid={apis['weather_key']}&units=metric"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.warning(f"Using simulated weather data: {str(e)}")
    
    # Simulated weather data
    days = min(duration, 5)
    conditions = ['Clear', 'Partly Cloudy', 'Cloudy', 'Light Rain', 'Sunny']
    
    return {
        'list': [
            {
                'dt': int((datetime.now() + timedelta(days=i)).timestamp()),
                'dt_txt': (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=i)).strftime('%Y-%m-%d'),
                'main': {
                    'temp': 18 + (i * 2) + (i % 2 * 3),
                    'feels_like': 17 + (i * 2),
                    'temp_min': 15 + (i * 2),
                    'temp_max': 22 + (i * 2),
                    'humidity': 60 + (i * 5)
                },
                'weather': [{
                    'main': conditions[i % 5],
                    'description': conditions[i % 5].lower(),
                    'icon': '01d'
                }],
                'wind': {'speed': 3.5 + i}
            } for i in range(days)
        ],
        'city': {
            'name': destination,
            'country': 'XX'
        }
    }

def get_attractions_from_amadeus(apis, destination):
    '''Fetch attractions from Amadeus API'''
    if apis['amadeus']:
        try:
            location_response = apis['amadeus'].reference_data.locations.get(
                keyword=destination,
                subType='CITY'
            )
            
            if location_response.data:
                lat = location_response.data[0]['geoCode']['latitude']
                lon = location_response.data[0]['geoCode']['longitude']
                
                poi_response = apis['amadeus'].shopping.activities.get(
                    latitude=lat,
                    longitude=lon
                )
                
                attractions = []
                for activity in poi_response.data[:15]:
                    attractions.append({
                        'name': activity.get('name', 'Attraction'),
                        'rating': activity.get('rating', 4.5),
                        'price': float(activity.get('price', {}).get('amount', 20)),
                        'duration': activity.get('duration', '2-3 hours'),
                        'description': activity.get('shortDescription', 'Popular attraction')
                    })
                
                return attractions
        except Exception as e:
            st.warning(f"Amadeus POI fetch failed: {str(e)}")
    
    return None

def get_attractions_from_gemini(apis, destination, interests):
    '''Generate attractions using Gemini AI'''
    if apis['gemini']:
        try:
            prompt = f'''
Generate a list of 15 real, popular attractions in {destination} that match these interests: {', '.join(interests)}.

For each attraction, provide in this EXACT JSON format:
[
  {{"name": "Attraction Name", "rating": 4.5, "price": 20, "duration": "2-3 hours", "description": "brief description"}},
  ...
]

Rules:
- Include REAL places that exist in {destination}
- Mix of free and paid attractions
- Prices in USD
- Variety of durations
- Match user interests: {', '.join(interests)}

Return ONLY the JSON array, no other text.
'''
            response = apis['gemini'].generate_content(prompt)
            response_text = response.text.strip()
            
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            return json.loads(response_text)
        except Exception as e:
            st.warning(f"AI attraction generation failed: {str(e)}")
    
    return None

def generate_generic_attractions(destination, interests):
    '''Generate generic but contextual attractions'''
    attraction_templates = {
        'Culture & Art': [
            (f'{destination} National Museum', 15, '2-3 hours', 'Main museum featuring local art'),
            (f'{destination} Art Gallery', 12, '1-2 hours', 'Contemporary art exhibitions'),
            (f'Cultural Quarter of {destination}', 0, '2-3 hours', 'Historic cultural district')
        ],
        'Food & Gastronomy': [
            (f'{destination} Food Market', 0, '2 hours', 'Famous local food market'),
            (f'Cooking Class in {destination}', 75, '3-4 hours', 'Learn traditional cooking'),
            (f'{destination} Street Food Tour', 45, '3 hours', 'Best street food spots')
        ],
        'Adventure & Outdoor': [
            (f'{destination} Outdoor Park', 0, '3-4 hours', 'Popular outdoor park'),
            (f'Adventure Activities near {destination}', 60, '4 hours', 'Hiking and sports'),
            (f'{destination} Nature Trail', 10, '2-3 hours', 'Scenic trails')
        ],
        'History & Heritage': [
            (f'Historic Center of {destination}', 0, '3 hours', 'Heritage landmarks'),
            (f'{destination} Historical Museum', 15, '2 hours', 'City history museum'),
            (f'Heritage Walking Tour {destination}', 25, '2.5 hours', 'Guided historic tour')
        ],
        'Shopping': [
            (f'{destination} Main Shopping Street', 0, '2-3 hours', 'Popular shopping'),
            (f'{destination} Local Market', 0, '2 hours', 'Traditional market'),
            (f'{destination} Shopping Mall', 0, '3 hours', 'Modern shopping center')
        ],
        'Nature & Wildlife': [
            (f'{destination} Botanical Garden', 10, '2 hours', 'Beautiful gardens'),
            (f'{destination} Zoo/Wildlife Park', 25, '3-4 hours', 'Wildlife attraction'),
            (f'Nature Reserve near {destination}', 15, '3 hours', 'Protected area')
        ],
        'Relaxation': [
            (f'{destination} Spa Center', 80, '2-3 hours', 'Wellness treatments'),
            (f'{destination} Waterfront', 0, '2-3 hours', 'Relaxing waterfront'),
            (f'{destination} Viewpoint', 0, '1-2 hours', 'Best sunset views')
        ]
    }
    
    attractions = []
    for interest in interests:
        if interest in attraction_templates:
            for name, price, duration, desc in attraction_templates[interest]:
                attractions.append({
                    'name': name,
                    'rating': round(4.3 + (len(attractions) * 0.1), 1),
                    'price': price,
                    'duration': duration,
                    'description': desc
                })
    
    # Add universal attractions
    universal = [
        (f'{destination} City Center', 0, '2-3 hours', 4.6, 'Main city center'),
        (f'Best Restaurants in {destination}', 40, '2 hours', 4.7, 'Top dining'),
        (f'{destination} Observation Deck', 20, '1 hour', 4.5, 'Panoramic views'),
    ]
    
    for name, price, duration, rating, desc in universal[:5]:
        attractions.append({
            'name': name,
            'rating': rating,
            'price': price,
            'duration': duration,
            'description': desc
        })
    
    return attractions[:15]
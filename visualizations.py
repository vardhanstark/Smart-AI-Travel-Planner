import streamlit as st
import plotly.express as px
import pandas as pd

def render_budget_visualizations(result):
    '''Render budget allocation charts'''
    st.header("💰 Budget Allocation & Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Planned Budget Distribution")
        budget_data = result['budget_breakdown']
        fig = px.pie(
            values=list(budget_data.values()),
            names=[k.title() for k in budget_data.keys()],
            title="Budget Allocation Strategy",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Actual Costs")
        actual_costs = result['actual_costs']
        
        st.metric("✈️ Flights", f"${actual_costs['flights']:.2f}")
        st.metric("🏨 Hotels", f"${actual_costs['hotels']:.2f}")
        st.metric("🎯 Activities & Food", f"${actual_costs['activities_food']:.2f}")
        st.metric("💵 Total Spent", f"${actual_costs['total_used']:.2f}", 
                 delta=f"${result['summary']['total_budget'] - actual_costs['total_used']:.2f} remaining")
    
    st.markdown("---")

def render_weather_charts(result, insights):
    '''Render weather forecast charts'''
    st.header("🌤️ Weather Forecast")
    
    weather_data = result['weather_summary']['list']
    weather_df = pd.DataFrame([{
        'Date': w['dt_txt'],
        'Temperature (°C)': w['main']['temp'],
        'Condition': w['weather'][0]['main'],
        'Humidity (%)': w['main']['humidity']
    } for w in weather_data])
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.line(
            weather_df, 
            x='Date', 
            y='Temperature (°C)', 
            title='Temperature Trend',
            markers=True,
            line_shape='spline'
        )
        fig.update_layout(hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            weather_df,
            x='Date',
            y='Humidity (%)',
            title='Humidity Levels',
            color='Humidity (%)',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    if insights['weather_alerts'] and insights['weather_alerts'][0] != 'No rain expected':
        st.warning(f"⚠️ **Weather Alerts:** Rain expected on {', '.join(insights['weather_alerts'][:2])}")
    
    st.markdown("---")
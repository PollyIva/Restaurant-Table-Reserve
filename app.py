import streamlit as st
from restaurant import Restaurant
from pages import status_page, tables_page, booking_page

# Initialize app state
if 'restaurant' not in st.session_state:
    st.session_state['restaurant'] = Restaurant()

restaurant = st.session_state['restaurant']

# Navigation between pages
page = st.sidebar.radio("Page", ["Booking", "Tables", "Status"])

if page == "Booking":
    booking_page(restaurant)

elif page == "Tables":
    tables_page(restaurant)

elif page == "Status":
    status_page(restaurant)
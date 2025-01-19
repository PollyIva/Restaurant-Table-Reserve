import streamlit as st
from restaurant import Restaurant
from datetime import datetime, timedelta
import time

def booking_page(restaurant: Restaurant) -> None:
    """
    Manages bookings in the app.

    - Provides a form for creating new bookings with client details, booking times, and table selection.
    - Displays the current status of all tables and allows users to delete bookings.
    - Releases tables with expired bookings.

    Args:
        restaurant (Restaurant): The restaurant instance containing table and booking information.
    """
    #Release tables with expired bookings
    restaurant.release_expired_bookings()

    st.header("Booking")

    # Form for creating a new booking
    with st.form("booking_form"):
        client_name = st.text_input("Input name")
        phone = st.text_input("Input phone")

        # Fields for booking time
        col1, col2 = st.columns([1, 1])
        with col1:
            start_time = st.time_input("From")
        with col2:
            period = st.number_input("Period", min_value=0, step=1)

        # Available tables sorted by name
        available_tables = sorted(
            [table for table in restaurant.tables if not table.booked],
            key=lambda t: t.name
        )

        # Dropdown for choosing an available table
        table_view = [f"{table.name} - {table.seats} seats" for table in available_tables]
        selected_table = st.selectbox("Select table", table_view)

        # Form submission button
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            # Convert entered time to datetime object
            start_datetime = datetime.combine(datetime.today(), start_time)
            end_datetime = start_datetime + timedelta(hours=period)
            
            # Find the selected table
            chosen_table = next((table for table in restaurant.tables if f"{table.name} - {table.seats} seats" == selected_table), None)
            
            if chosen_table:
                # Create a booking
                booking = restaurant.create_reservation(client_name, phone, start_datetime, end_datetime, chosen_table.name)
                if booking:
                    st.success(f"Booking created for {client_name} at {selected_table}.")
                else:
                    st.error("Could not create the booking.")
            else:
                st.error("Selected table is not available or does not exist.")


    st.write(" ")

    # Display table statuses
    sorted_tables = sorted(restaurant.tables, key=lambda t: t.name)
    for table in sorted_tables:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"{table.name} - {table.seats} seats")
        with col2:
            status = "Free" if not table.booked else "Occupied"
            st.write(status)
        with col3:
            if st.button("Delete", key=f"delete_booking_{table.name}"):
                # Delete booking and release table
                booking_to_remove = next(
                    (booking for booking in restaurant.bookings if booking.table == table), 
                    None
                )
                if booking_to_remove:
                    restaurant.bookings.remove(booking_to_remove)
                    table.release()
                    st.success(f"Booking for {table.name} has been deleted.")
                else:
                    table.release()
                    st.success(f"{table.name} has been released.")


def status_page(restaurant: Restaurant) -> None:
    """
    Displays the current status of all tables in the restaurant.

    - Releases expired bookings to update table availability.
    - Shows whether each table is free or occupied, along with the remaining time for occupied tables.
    - Provides a summary of the number of free tables and seats available.

    Args:
        restaurant (Restaurant): The restaurant instance containing table and booking information.
    """
    # Release expired bookings
    restaurant.release_expired_bookings()

    st.header("Status")

    free_tables = 0
    free_seats = 0

    sorted_tables = sorted(restaurant.tables, key=lambda table: table.name)

    # Display table statuses
    for table in sorted_tables:
        col1, col2 = st.columns([2, 1])  
        with col1:
            st.write(f"**{table.name}** - {table.seats} seats")
        with col2:
            if table.booked:
                # Find the booking linked to this table
                booking = next((b for b in restaurant.bookings if b.table == table), None)
                if booking:
                    # Calculate the remaining booking time
                    time_remaining = (booking.end_time - datetime.now()).seconds // 60
                    st.write(f"**Occupied** ({time_remaining} min left)")
                else:
                    st.write("**Occupied** (No booking)")
            else:
                st.write("**Free**")
                free_tables += 1
                free_seats += table.seats

    # Summary of available tables and seats
    st.write(f"Number of free tables  -  {free_tables}")
    st.write(f"Number of free seats  -  {free_seats}")





def tables_page(restaurant: Restaurant) -> None:
    """
    Manages the addition, management, and updating of tables.

    - Allows selecting an existing table and performing actions such as taking, releasing, or deleting it.
    - Provides functionality to add new tables with a specified name and number of seats.
    - Ensures expired bookings are released to maintain accurate table status.

    Args:
        restaurant (Restaurant): The restaurant instance containing table and booking information.
    """
    # Release expired bookings
    restaurant.release_expired_bookings()

    st.header("Tables")

    # Dropdown to select a table
    table_view = [f"{table.name} - {table.seats}" for table in restaurant.tables]
    selected_table = st.selectbox("Select a table", table_view)

    # Find the selected table
    chosen_table = next((table for table in restaurant.tables if f"{table.name} - {table.seats}" == selected_table), None)

    # Table management buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
       if st.button("Take the table"):
            if chosen_table and not chosen_table.booked:
                # Create a temporary booking
                temp_booking = restaurant.create_reservation(
                    client_name="Temporary",
                    phone="N/A",
                    start_time=datetime.now(),
                    end_time=datetime.now() + timedelta(hours=1),
                    table_name=chosen_table.name
                )
                chosen_table.take()
                if temp_booking:
                    st.success(f"{chosen_table.name} is now occupied with a temporary (1 hour) booking.")
                else:
                    st.error(f"Failed to create a temporary booking for {chosen_table.name}.")
            else:
                st.error(f"{chosen_table.name} is already booked.")
    with col2:
        if st.button("Release the table"):
            if chosen_table:
                # Remove booking if it exists
                booking_to_remove = next(
                    (b for b in restaurant.bookings if b.table == chosen_table), 
                    None
                )
                if booking_to_remove:
                    restaurant.bookings.remove(booking_to_remove)
                chosen_table.release()
                st.success(f"{selected_table} is now available.")
    with col3:
        if st.button("Delete"):
            if chosen_table in restaurant.tables:
                # Remove booking if it exists
                booking_to_remove = next(
                    (b for b in restaurant.bookings if b.table == chosen_table), 
                    None
                )
                if booking_to_remove:
                    restaurant.bookings.remove(booking_to_remove)
                restaurant.tables.remove(chosen_table)
                st.success(f"{selected_table} has been deleted.")
                time.sleep(2)
                st.rerun()


    # Form to add a new table
    st.subheader("Add a New Table")
    table_name = st.text_input("Name of table")
    table_seats = st.number_input("Number of seats", min_value=1, step=1, value=4)

    if st.button("Add"):
        if table_name:
            # Check if there is a table with the same name
            existing_table = next((table for table in restaurant.tables if table.name == table_name), None)
            if existing_table:
                st.error(f"A table with the name '{table_name}' already exists. Please choose a different name.")
            else:
                restaurant.add_table(table_name, table_seats)
                st.success(f"{table_name} with {table_seats} seats has been added.")
                time.sleep(3)
                st.rerun()  # Updating the page after adding a new table

        else:
            st.error("Please enter a valid table name.")

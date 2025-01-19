from datetime import datetime

class Table:
    def __init__(self, name, seats):
        self._name = name 
        self._seats = seats
        self.__booked = False

    @property
    def name(self):
        return self._name

    @property
    def seats(self):
        return self._seats

    @property
    def booked(self):
        return self.__booked

    def take(self):
        self.__booked = True

    def release(self):
        self.__booked = False

class Booking:
    def __init__(self, client_name, phone, start_time, end_time, table):
        self.client_name = client_name
        self.phone = phone
        self.start_time = start_time
        self.end_time = end_time
        self.table = table

class Restaurant:
    def __init__(self):
        self.tables = []
        self.bookings = []

    def add_table(self, name, seats):
        table = Table(name, seats)
        self.tables.append(table)
    
    def create_reservation(self, client_name, phone, start_time, end_time, table_name):
        # Looking for a table by name
        table = next((table for table in self.tables if table.name == table_name), None)
        if table and not table.booked: # Checking if it is available
            table.take()
            booking = Booking(client_name, phone, start_time, end_time, table)
            self.bookings.append(booking)
            return booking
        return None  # If the table is not found or has already been booked

        
    def release_expired_bookings(self):
        now = datetime.now()
        for booking in self.bookings:
            if booking.end_time < now:
                booking.table.release()
                self.bookings.remove(booking)

    def current_status(self):
        return [(booking.client_name, booking.table.name, booking.start_time, booking.end_time)
                for booking in self.bookings]
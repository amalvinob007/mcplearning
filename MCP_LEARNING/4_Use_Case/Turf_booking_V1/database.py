import sqlite3
import os
from datetime import datetime, timedelta

class TurfDatabase:
    def __init__(self, db_name="turf_booking.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """Initialize the turf booking database with tables and sample data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create turfs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS turfs (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                hourly_rate REAL NOT NULL,
                capacity INTEGER NOT NULL,
                facilities TEXT
            )
        """)
        
        # Create bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY,
                turf_id INTEGER NOT NULL,
                customer_name TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                total_cost REAL NOT NULL,
                status TEXT DEFAULT 'confirmed',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (turf_id) REFERENCES turfs (id)
            )
        """)
        
        # Insert sample turfs if table is empty
        cursor.execute("SELECT COUNT(*) FROM turfs")
        if cursor.fetchone()[0] == 0:
            sample_turfs = [
                (1, "Green Valley Turf", "Chennai - Velachery", 800.0, 22, "Floodlights, Parking, Restrooms"),
                (2, "City Sports Arena", "Chennai - T Nagar", 1200.0, 22, "Floodlights, Parking, Restrooms, Cafeteria"),
                (3, "Phoenix Turf", "Chennai - OMR", 1000.0, 18, "Floodlights, Parking, Restrooms, Equipment Rental"),
                (4, "Champions Ground", "Chennai - Adyar", 1500.0, 22, "Premium Grass, Floodlights, Parking, Restrooms, Changing Rooms"),
                (5, "Sportz Zone", "Chennai - Porur", 900.0, 20, "Floodlights, Parking, Restrooms")
            ]
            
            cursor.executemany(
                "INSERT INTO turfs (id, name, location, hourly_rate, capacity, facilities) VALUES (?, ?, ?, ?, ?, ?)",
                sample_turfs
            )
        
        # Insert sample bookings if table is empty
        cursor.execute("SELECT COUNT(*) FROM bookings")
        if cursor.fetchone()[0] == 0:
            # Get today's date and create some sample bookings
            today = datetime.now()
            tomorrow = today + timedelta(days=1)
            day_after = today + timedelta(days=2)
            
            sample_bookings = [
                (1, 1, "Rajesh Kumar", "9876543210", today.strftime("%Y-%m-%d"), "06:00", "08:00", 1600.0, "confirmed"),
                (2, 1, "Priya Sharma", "8765432109", today.strftime("%Y-%m-%d"), "18:00", "20:00", 1600.0, "confirmed"),
                (3, 2, "Team Alpha", "7654321098", tomorrow.strftime("%Y-%m-%d"), "09:00", "11:00", 2400.0, "confirmed"),
                (4, 3, "Mumbai Warriors", "6543210987", tomorrow.strftime("%Y-%m-%d"), "16:00", "18:00", 2000.0, "confirmed"),
                (5, 4, "Chennai FC", "5432109876", day_after.strftime("%Y-%m-%d"), "10:00", "12:00", 3000.0, "confirmed")
            ]
            
            cursor.executemany(
                "INSERT INTO bookings (id, turf_id, customer_name, customer_phone, booking_date, start_time, end_time, total_cost, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                sample_bookings
            )
        
        conn.commit()
        conn.close()
        print("Turf booking database initialized successfully!")

def setup_database():
    """Setup function to initialize database"""
    db = TurfDatabase()
    return db

if __name__ == "__main__":
    # Initialize database when run directly
    setup_database()
    print("Database setup completed!")
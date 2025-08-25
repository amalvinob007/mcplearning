import sqlite3
import json
from datetime import datetime, timedelta
from fastmcp import FastMCP
from database import TurfDatabase
from resources.server_all import turf_all, all_booking, check_availability, book_turf

# Initialize MCP server and database
mcp = FastMCP("turf-booking-system")
db = TurfDatabase()

# Convert all resources to tools
@mcp.tool()
def get_all_turfs() -> str:
    """
    Get all available turfs with their details including ID, name, location, rate, capacity, and facilities
    
    Returns:
        str: Formatted string containing all turf information
    """
    return turf_all()

@mcp.tool()
def get_all_bookings() -> str:
    """
    Get all bookings with turf details (without customer PII for privacy)
    
    Returns:
        str: Formatted string containing all booking information with turf names, dates, times, costs, and status
    """
    return all_booking()

@mcp.tool()
def check_turf_availability(turf_id: int, date: str) -> str:
    """
    Check availability for a specific turf on a specific date
    
    Args:
        turf_id: ID of the turf to check availability for
        date: Date to check availability (YYYY-MM-DD format)
        
    Returns:
        str: Formatted availability information showing booked and available time slots
    """
    return check_availability(str(turf_id), date)

@mcp.tool()
def make_booking(turf_id: int, customer_name: str, customer_phone: str, 
                booking_date: str, start_time: str, end_time: str) -> str:
    """
    Make a new turf booking
    
    Args:
        turf_id: ID of the turf to book
        customer_name: Name of the customer
        customer_phone: Phone number of the customer
        booking_date: Date of booking (YYYY-MM-DD format)
        start_time: Start time (HH:MM format)
        end_time: End time (HH:MM format)
        
    Returns:
        str: Booking confirmation with details or error message
    """
    return book_turf(turf_id, customer_name, customer_phone, 
                     booking_date, start_time, end_time)

if __name__ == "__main__":
    mcp.run()
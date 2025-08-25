import sqlite3
import json
from datetime import datetime, timedelta
from fastmcp import FastMCP
from database import TurfDatabase
from resources.server_all import turf_all, all_booking, check_availability, book_turf

# Initialize MCP server and database
mcp = FastMCP("turf-booking-system")
db = TurfDatabase()

@mcp.resource("turf://all")
def get_all_turfs() -> str:
    """Get all available turfs"""
    return turf_all()
    


@mcp.resource("turf://bookings/all")
def get_all_bookings() -> str:
    """Get all bookings with turf details (without customer PII)"""
    return all_booking()


@mcp.resource("turf://availability/{turf_id}/{date}")
def check_turf_availability(turf_id: str, date: str) -> str:
    """Check availability for a specific turf on a specific date"""
    return check_availability(turf_id, date)



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
    """
    return book_turf(turf_id, customer_name, customer_phone, 
                     booking_date, start_time, end_time)


if __name__ == "__main__":
    mcp.run()
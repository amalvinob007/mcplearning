from datetime import datetime, timedelta
from database import TurfDatabase

db = TurfDatabase()

def turf_all():
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM turfs ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "No turfs available"
    
    result = "🏟️ Available Turfs:\n\n"
    for row in rows:
        result += f"ID: {row[0]}\n"
        result += f"Name: {row[1]}\n"
        result += f"Location: {row[2]}\n"
        result += f"Rate: ₹{row[3]}/hour\n"
        result += f"Capacity: {row[4]} players\n"
        result += f"Facilities: {row[5]}\n"
        result += "-" * 40 + "\n"
    
    return result


def all_booking():
    conn = db.get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT b.id, t.name, 
               b.booking_date, b.start_time, b.end_time, 
               b.total_cost, b.status
        FROM bookings b
        JOIN turfs t ON b.turf_id = t.id
        ORDER BY b.booking_date DESC, b.start_time
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "No bookings found"
    
    result = "📅 All Bookings:\n\n"
    for row in rows:
        result += f"Booking ID: {row[0]}\n"
        result += f"Turf: {row[1]}\n"
        result += f"Date: {row[2]}\n"
        result += f"Time: {row[3]} - {row[4]}\n"
        result += f"Cost: ₹{row[5]}\n"
        result += f"Status: {row[6]}\n"
        result += "-" * 40 + "\n"
    
    return result


def check_availability(turf_id, date):
    try:
        turf_id_int = int(turf_id)
        # Validate date format
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return f"Invalid turf ID or date format. Use YYYY-MM-DD for date."
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Get turf details
    cursor.execute("SELECT name, location, hourly_rate FROM turfs WHERE id = ?", (turf_id_int,))
    turf = cursor.fetchone()
    
    if not turf:
        conn.close()
        return f"Turf with ID {turf_id} not found"
    
    # Get bookings for that date (⚠️ Removed customer_name)
    cursor.execute("""
        SELECT start_time, end_time, status 
        FROM bookings 
        WHERE turf_id = ? AND booking_date = ? AND status = 'confirmed'
        ORDER BY start_time
    """, (turf_id_int, date))
    
    bookings = cursor.fetchall()
    conn.close()
    
    result = f"🏟️ {turf[0]} - {turf[1]}\n"
    result += f"📅 Availability for {date}\n"
    result += f"💰 Rate: ₹{turf[2]}/hour\n\n"
    
    if not bookings:
        result += "✅ Fully Available (6:00 AM - 11:00 PM)"
    else:
        result += "🔴 Booked Slots:\n"
        for booking in bookings:
            result += f"• {booking[0]} - {booking[1]}\n"   # ❌ No customer name shown
        
        result += "\n✅ Available Slots:\n"
        # Simple logic to show available slots (6 AM to 11 PM)
        all_hours = [f"{i:02d}:00" for i in range(6, 23)]
        booked_hours = []
        
        for booking in bookings:
            start_hour = int(booking[0].split(":")[0])
            end_hour = int(booking[1].split(":")[0])
            for h in range(start_hour, end_hour):
                booked_hours.append(f"{h:02d}:00")
        
        available_hours = [h for h in all_hours if h not in booked_hours]
        if available_hours:
            for hour in available_hours:
                result += f"• {hour} - {int(hour.split(':')[0])+1:02d}:00\n"
        else:
            result += "No slots available"
    
    return result


def book_turf(turf_id: int, customer_name: str, customer_phone: str, 
                booking_date: str, start_time: str, end_time: str) -> str:
    try:
        # Validate date and time formats
        booking_date_obj = datetime.strptime(booking_date, "%Y-%m-%d")
        start_time_obj = datetime.strptime(start_time, "%H:%M")
        end_time_obj = datetime.strptime(end_time, "%H:%M")
        
        # Check if booking is not in the past
        booking_datetime = datetime.combine(booking_date_obj.date(), start_time_obj.time())
        if booking_datetime < datetime.now():
            return "❌ Cannot book slots in the past"
        
        # Check if end time is after start time
        if end_time_obj <= start_time_obj:
            return "❌ End time must be after start time"
        
    except ValueError:
        return "❌ Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time"
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check if turf exists and get rate
    cursor.execute("SELECT name, hourly_rate FROM turfs WHERE id = ?", (turf_id,))
    turf = cursor.fetchone()
    
    if not turf:
        conn.close()
        return f"❌ Turf with ID {turf_id} not found"
    
    # Check for conflicting bookings
    cursor.execute("""
        SELECT COUNT(*) FROM bookings 
        WHERE turf_id = ? AND booking_date = ? 
        AND status = 'confirmed'
        AND NOT (end_time <= ? OR start_time >= ?)
    """, (turf_id, booking_date, start_time, end_time))
    
    conflicts = cursor.fetchone()[0]
    
    if conflicts > 0:
        conn.close()
        return f"❌ Time slot conflicts with existing booking. Check availability first."
    
    # Calculate duration and total cost
    duration_hours = (end_time_obj - start_time_obj).seconds / 3600
    total_cost = duration_hours * turf[1]
    
    # Insert booking
    cursor.execute("""
        INSERT INTO bookings (turf_id, customer_name, customer_phone, booking_date, 
                            start_time, end_time, total_cost, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'confirmed')
    """, (turf_id, customer_name, customer_phone, booking_date, start_time, end_time, total_cost))
    
    booking_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    result = f"✅ Booking Confirmed!\n\n"
    result += f"Booking ID: {booking_id}\n"
    result += f"Turf: {turf[0]}\n"
    result += f"Customer: {customer_name} ({customer_phone})\n"
    result += f"Date: {booking_date}\n"
    result += f"Time: {start_time} - {end_time}\n"
    result += f"Duration: {duration_hours} hours\n"
    result += f"Total Cost: ₹{total_cost}\n"
    
    return result
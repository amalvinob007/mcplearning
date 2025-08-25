import asyncio
from datetime import datetime, timedelta

async def test_resource(session):
    print("=" * 60)
    print("🔍 TESTING MCP RESOURCES (Read Operations)")
    print("=" * 60)
    
    # 1. Test all turfs
    print("\n1. 🏟️ Getting All Turfs:")
    print("-" * 30)
    res = await session.read_resource("turf://all")
    print(res.contents[0].text)
    
    # 2. Test all bookings
    print("\n2. 📅 Getting All Bookings:")
    print("-" * 30)
    res = await session.read_resource("turf://bookings/all")
    print(res.contents[0].text)
    
    # 3. Test turf availability
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"\n3. 🔍 Checking Availability for Turf 1 on {today}:")
    print("-" * 50)
    res = await session.read_resource(f"turf://availability/1/{today}")
    print(res.contents[0].text)
    
    print(f"\n4. 🔍 Checking Availability for Turf 2 on {tomorrow}:")
    print("-" * 50)
    res = await session.read_resource(f"turf://availability/2/{tomorrow}")
    print(res.contents[0].text)



async def test_tool(session):
    print("\n" + "=" * 60)
    print("🛠️ TESTING MCP TOOLS (Write Operations)")
    print("=" * 60)
    
    # Get tomorrow's date for booking
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 1. Test making a booking
    print("\n1. 📝 Making a New Booking:")
    print("-" * 30)
    try:
        result = await session.call_tool(
            "make_booking",
            arguments={
                "turf_id": 1,
                "customer_name": "John Doe",
                "customer_phone": "9999888877",
                "booking_date": tomorrow,
                "start_time": "14:00",
                "end_time": "16:00"
            }
        )
        print(result.content[0].text)
        
        # Store booking ID for cancellation test
        booking_text = result.content[0].text
        if "Booking ID:" in booking_text:
            booking_id = int(booking_text.split("Booking ID: ")[1].split("\n")[0])
            print(f"\n📌 Booking ID {booking_id} will be used for cancellation test")
        
    except Exception as e:
        print(f"❌ Error making booking: {e}")
    
    # 2. Test booking with conflict (should fail)
    print("\n2. ❌ Testing Conflicting Booking (Should Fail):")
    print("-" * 45)
    try:
        result = await session.call_tool(
            "make_booking",
            arguments={
                "turf_id": 1,
                "customer_name": "Jane Smith",
                "customer_phone": "8888777766",
                "booking_date": tomorrow,
                "start_time": "15:00",  # Overlaps with previous booking
                "end_time": "17:00"
            }
        )
        print(result.content[0].text)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. Test past booking (should fail)
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    print("\n3. ❌ Testing Past Date Booking (Should Fail):")
    print("-" * 45)
    try:
        result = await session.call_tool(
            "make_booking",
            arguments={
                "turf_id": 2,
                "customer_name": "Past Booker",
                "customer_phone": "7777666655",
                "booking_date": yesterday,
                "start_time": "10:00",
                "end_time": "12:00"
            }
        )
        print(result.content[0].text)
    except Exception as e:
        print(f"❌ Error: {e}")


async def interact_mode(session):
    print("\n" + "=" * 60)
    print("🎯 INTERACTIVE MODE")
    print("=" * 60)
    print("\nAvailable Commands:")
    print("📋 Resources (Read Operations):")
    print("  - turfs: Show all turfs")
    print("  - bookings: Show all bookings") 
    print("  - availability <turf_id> <date>: Check availability")
    print("\n🛠️ Tools (Write Operations):")
    print("  - book: Make a new booking (interactive)")
    print("\n💡 Other:")
    print("  - help: Show this help")
    print("  - quit: Exit interactive mode")
    
    while True:
        try:
            user_input = input("\n🎮 Command: ").strip().lower()
            
            if user_input == "quit" or user_input == "q":
                print("👋 Goodbye!")
                break
            elif user_input == "help":
                print("\n📋 Available commands: turfs, bookings, availability, book, help, quit")
                continue
            elif user_input == "turfs":
                res = await session.read_resource("turf://all")
                print(res.contents[0].text)
            elif user_input == "bookings":
                res = await session.read_resource("turf://bookings/all")
                print(res.contents[0].text)
            elif user_input.startswith("availability"):
                parts = user_input.split()
                if len(parts) == 3:
                    turf_id, date = parts[1], parts[2]
                    res = await session.read_resource(f"turf://availability/{turf_id}/{date}")
                    print(res.contents[0].text)
                else:
                    print("❌ Usage: availability <turf_id> <date> (YYYY-MM-DD)")

            elif user_input == "book":
                # Interactive booking
                try:
                    print("\n📝 Making a New Booking:")
                    turf_id = int(input("Turf ID: "))
                    customer_name = input("Customer Name: ")
                    customer_phone = input("Customer Phone: ")
                    booking_date = input("Date (YYYY-MM-DD): ")
                    start_time = input("Start Time (HH:MM): ")
                    end_time = input("End Time (HH:MM): ")
                    
                    result = await session.call_tool(
                        "make_booking",
                        arguments={
                            "turf_id": turf_id,
                            "customer_name": customer_name,
                            "customer_phone": customer_phone,
                            "booking_date": booking_date,
                            "start_time": start_time,
                            "end_time": end_time
                        }
                    )
                    print(result.content[0].text)
                except ValueError:
                    print("❌ Invalid input format")
                except Exception as e:
                    print(f"❌ Error: {e}")
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

import streamlit as st
import asyncio
import sys
import os
from datetime import datetime, date, timedelta
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your existing agent and prompt processor
from turf_agent import setup_turf_agent
from prompt_server import process_prompt_request, initialize_processor

# Page configuration
st.set_page_config(
    page_title="🏟️ Turf Booking System",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    .chat-message {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    .prompt-message {
        background-color: #e8f5e8;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #2196F3;
    }
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session states
def initialize_session_state():
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'prompt_messages' not in st.session_state:
        st.session_state.prompt_messages = []
    if 'agent_ready' not in st.session_state:
        st.session_state.agent_ready = False
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'client' not in st.session_state:
        st.session_state.client = None

# Async wrapper for Streamlit
def run_async(coro):
    """Helper function to run async functions in Streamlit"""
    try:
        # Try to get the current event loop
        loop = asyncio.get_running_loop()
        # If we're already in an async context, we need to use a different approach
        import concurrent.futures
        import threading
        
        def run_in_thread():
            # Create a new event loop for this thread
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()
        
        # Run the coroutine in a separate thread with its own event loop
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result(timeout=60)  # 60 second timeout
            
    except RuntimeError:
        # No event loop running, safe to create one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

# Initialize the turf agent
def setup_agent():
    """Setup the turf agent - using synchronous approach"""
    try:
        def setup_sync():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                from turf_agent import setup_turf_agent
                agent, client = loop.run_until_complete(setup_turf_agent())
                return agent, client, True
            except Exception as e:
                st.error(f"Setup error: {str(e)}")
                return None, None, False
            finally:
                loop.close()
        
        return setup_sync()
    except Exception as e:
        st.error(f"Failed to setup agent: {str(e)}")
        return None, None, False

# Main app
def main():
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏟️ Turf Booking System</h1>
        <p>Chat with our AI agent or use smart prompts for quick actions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for mode selection
    st.sidebar.title("🎯 Choose Mode")
    mode = st.sidebar.radio(
        "Select how you want to interact:",
        ["💬 Chat Mode", "🎯 Smart Prompts Mode"],
        index=0
    )
    
    if mode == "💬 Chat Mode":
        chat_mode()
    else:
        smart_prompts_mode()

def chat_mode():
    """Traditional chatbot interface"""
    st.header("💬 Chat with Turf Booking Assistant")
    
    # Setup agent if not ready
    if not st.session_state.agent_ready:
        with st.spinner("🤖 Setting up Turf Booking Agent..."):
            agent, client, success = setup_agent()
            if success:
                st.session_state.agent = agent
                st.session_state.client = client
                st.session_state.agent_ready = True
                st.success("✅ Agent ready!")
            else:
                st.error("❌ Failed to setup agent")
                return
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about turfs, bookings, or make a reservation..."):
        # Add user message to chat
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Process with agent
        with st.chat_message("assistant"):
            with st.spinner("🤖 Processing..."):
                try:
                    def process_message():
                        # Create a new event loop for this operation
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            response = loop.run_until_complete(
                                st.session_state.agent.ainvoke(
                                    {"messages": [{"role": "user", "content": prompt}]}
                                )
                            )
                            return response
                        finally:
                            loop.close()
                    
                    response = process_message()
                    
                    # Get the last assistant message
                    last_message = response["messages"][-1]
                    assistant_response = last_message.content
                    
                    st.write(assistant_response)
                    
                    # Add assistant message to chat
                    st.session_state.chat_messages.append({
                        "role": "assistant", 
                        "content": assistant_response
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
    
    # Clear chat button
    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.chat_messages = []
        st.rerun()

def smart_prompts_mode():
    """Smart prompts interface with forms"""
    st.header("🎯 Smart Prompts - Quick Actions")
    
    # Initialize prompt processor
    if 'prompt_processor_ready' not in st.session_state:
        with st.spinner("🔄 Initializing prompt processor..."):
            try:
                run_async(initialize_processor())
                st.session_state.prompt_processor_ready = True
                st.success("✅ Prompt processor ready!")
            except Exception as e:
                st.error(f"❌ Failed to initialize prompt processor: {str(e)}")
                return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Quick Actions")
        
        # Check Availability Button
        if st.button("🔍 Check Turf Availability", use_container_width=True):
            st.session_state.show_availability_form = True
        
        # List Turfs Button
        if st.button("🏟️ View All Turfs", use_container_width=True):
            with st.spinner("🔄 Getting turf information..."):
                result = run_async(process_prompt_request("list-turfs", {}))
                st.session_state.prompt_messages.append({
                    "type": "prompt_result",
                    "action": "List Turfs",
                    "content": result
                })
                st.rerun()
        
        # View Bookings Button
        if st.button("📅 View Current Bookings", use_container_width=True):
            st.session_state.show_bookings_form = True
        
        # Make Booking Button
        if st.button("➕ Make New Booking", use_container_width=True):
            st.session_state.show_booking_form = True
        
        # Booking Summary Button
        if st.button("📊 Booking Summary", use_container_width=True):
            st.session_state.show_summary_form = True
    
    with col2:
        st.subheader("📝 Forms & Results")
        
        # Availability Check Form
        if st.session_state.get('show_availability_form', False):
            with st.form("availability_form"):
                st.write("**🔍 Check Turf Availability**")
                turf_id = st.number_input("Turf ID", min_value=1, value=1)
                check_date = st.date_input("Date", min_value=date.today())
                preferred_time = st.text_input("Preferred Time (optional)", placeholder="e.g., 14:00-16:00")
                
                if st.form_submit_button("Check Availability"):
                    args = {
                        "turf_id": str(turf_id),
                        "date": check_date.strftime("%Y-%m-%d"),
                        "preferred_time": preferred_time
                    }
                    
                    with st.spinner("🔄 Checking availability..."):
                        result = run_async(process_prompt_request("check-availability", args))
                        st.session_state.prompt_messages.append({
                            "type": "prompt_result",
                            "action": "Check Availability",
                            "args": args,
                            "content": result
                        })
                        st.session_state.show_availability_form = False
                        st.rerun()
        
        # Booking Form
        if st.session_state.get('show_booking_form', False):
            with st.form("booking_form"):
                st.write("**➕ Make New Booking**")
                turf_id = st.number_input("Turf ID", min_value=1, value=1)
                customer_name = st.text_input("Customer Name")
                customer_phone = st.text_input("Phone Number")
                booking_date = st.date_input("Booking Date", min_value=date.today())
                
                col1, col2 = st.columns(2)
                with col1:
                    start_time = st.time_input("Start Time")
                with col2:
                    end_time = st.time_input("End Time")
                
                if st.form_submit_button("Make Booking"):
                    if customer_name and customer_phone:
                        args = {
                            "turf_id": str(turf_id),
                            "customer_name": customer_name,
                            "customer_phone": customer_phone,
                            "booking_date": booking_date.strftime("%Y-%m-%d"),
                            "start_time": start_time.strftime("%H:%M"),
                            "end_time": end_time.strftime("%H:%M")
                        }
                        
                        with st.spinner("📝 Processing booking..."):
                            result = run_async(process_prompt_request("make-booking", args))
                            st.session_state.prompt_messages.append({
                                "type": "prompt_result",
                                "action": "Make Booking",
                                "args": args,
                                "content": result
                            })
                            st.session_state.show_booking_form = False
                            st.rerun()
                    else:
                        st.error("Please fill in customer name and phone number")
        
        # View Bookings Form
        if st.session_state.get('show_bookings_form', False):
            with st.form("bookings_form"):
                st.write("**📅 View Bookings (with filters)**")
                date_filter = st.date_input("Filter by Date (optional)", value=None)
                turf_filter = st.number_input("Filter by Turf ID (optional)", min_value=0, value=0)
                
                if st.form_submit_button("View Bookings"):
                    args = {}
                    if date_filter:
                        args["date_filter"] = date_filter.strftime("%Y-%m-%d")
                    if turf_filter > 0:
                        args["turf_filter"] = str(turf_filter)
                    
                    with st.spinner("📋 Getting bookings..."):
                        result = run_async(process_prompt_request("view-bookings", args))
                        st.session_state.prompt_messages.append({
                            "type": "prompt_result",
                            "action": "View Bookings",
                            "args": args,
                            "content": result
                        })
                        st.session_state.show_bookings_form = False
                        st.rerun()
        
        # Summary Form
        if st.session_state.get('show_summary_form', False):
            with st.form("summary_form"):
                st.write("**📊 Booking Summary**")
                turf_id = st.number_input("Turf ID for Summary", min_value=1, value=1)
                date_range = st.selectbox("Date Range", 
                    ["current", "this_week", "next_week", "this_month", "next_month"])
                
                if st.form_submit_button("Generate Summary"):
                    args = {
                        "turf_id": str(turf_id),
                        "date_range": date_range
                    }
                    
                    with st.spinner("📊 Generating summary..."):
                        result = run_async(process_prompt_request("booking-summary", args))
                        st.session_state.prompt_messages.append({
                            "type": "prompt_result",
                            "action": "Booking Summary",
                            "args": args,
                            "content": result
                        })
                        st.session_state.show_summary_form = False
                        st.rerun()
    
    # Display prompt results
    st.subheader("📨 Prompt Results")
    
    if st.session_state.prompt_messages:
        for i, message in enumerate(reversed(st.session_state.prompt_messages[-10:])):  # Show last 10
            with st.expander(f"🎯 {message['action']} - Result #{len(st.session_state.prompt_messages)-i}"):
                if message.get('args'):
                    st.write("**Parameters:**")
                    st.json(message['args'])
                st.write("**Result:**")
                st.markdown(f'<div class="prompt-message">{message["content"]}</div>', 
                           unsafe_allow_html=True)
    else:
        st.info("👆 Use the buttons above to perform quick actions!")
    
    # Clear results button
    if st.sidebar.button("🗑️ Clear Results"):
        st.session_state.prompt_messages = []
        st.rerun()

if __name__ == "__main__":
    main()
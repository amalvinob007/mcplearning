import streamlit as st
import sys
import os
from datetime import datetime, date, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import synchronous wrappers
from sync_agent import get_sync_agent

# Page configuration
st.set_page_config(
    page_title="🏟️ Turf Booking System",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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

def setup_agent():
    """Setup the agent if not already done"""
    if not st.session_state.agent_ready:
        with st.spinner("🤖 Setting up Turf Booking Agent..."):
            agent = get_sync_agent()
            success = agent.setup()
            
            if success:
                st.session_state.agent_ready = True
                st.success("✅ Agent ready!")
                return True
            else:
                st.error("❌ Failed to setup agent. Please check your .env file and try again.")
                return False
    return True

def execute_prompt_through_agent(prompt_text: str, action_name: str, args: dict = None):
    """Execute a prompt through the main agent and store result"""
    if not setup_agent():
        return
    
    with st.spinner(f"🔄 {action_name}..."):
        agent = get_sync_agent()
        result = agent.chat(prompt_text)
        
        st.session_state.prompt_messages.append({
            "type": "prompt_result",
            "action": action_name,
            "args": args,
            "content": result
        })
        st.rerun()

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
    
    if not setup_agent():
        return
    
    # Display chat messages
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
                agent = get_sync_agent()
                assistant_response = agent.chat(prompt)
                
                st.write(assistant_response)
                
                # Add assistant message to chat
                st.session_state.chat_messages.append({
                    "role": "assistant", 
                    "content": assistant_response
                })
    
    # Clear chat button
    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.chat_messages = []
        st.rerun()

def smart_prompts_mode():
    """Smart prompts interface with forms - all using the main agent"""
    st.header("🎯 Smart Prompts - Quick Actions")
    
    if not setup_agent():
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Quick Actions")
        
        # Check Availability Button
        if st.button("🔍 Check Turf Availability", use_container_width=True):
            st.session_state.show_availability_form = True
        
        # List Turfs Button
        if st.button("🏟️ View All Turfs", use_container_width=True):
            prompt_text = "Show me all available turfs with their details including ID, name, location, rate, capacity, and facilities."
            execute_prompt_through_agent(prompt_text, "List All Turfs")
        
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
                    
                    # Create prompt for the agent
                    time_context = f" for preferred time {preferred_time}" if preferred_time else ""
                    prompt_text = f"Check the availability of turf {turf_id} on {check_date.strftime('%Y-%m-%d')}{time_context}. Show me all available time slots along with any existing bookings. Also provide the turf details like location and rates."
                    
                    st.session_state.show_availability_form = False
                    execute_prompt_through_agent(prompt_text, "Check Availability", args)
        
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
                        
                        # Create prompt for the agent
                        prompt_text = f"""Please make a booking for turf {turf_id} with the following details:
Customer Name: {customer_name}
Phone: {customer_phone}
Date: {booking_date.strftime('%Y-%m-%d')}
Time: {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}

First check if the slot is available, then proceed with the booking and provide confirmation details including total cost."""
                        
                        st.session_state.show_booking_form = False
                        execute_prompt_through_agent(prompt_text, "Make Booking", args)
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
                    filter_text = ""
                    
                    if date_filter:
                        args["date_filter"] = date_filter.strftime("%Y-%m-%d")
                        filter_text += f" for date {date_filter.strftime('%Y-%m-%d')}"
                    if turf_filter > 0:
                        args["turf_filter"] = str(turf_filter)
                        filter_text += f" for turf ID {turf_filter}"
                    
                    # Create prompt for the agent
                    prompt_text = f"Show me all current bookings{filter_text}. Display the booking information in a clear, organized format including booking IDs, turf names, dates, times, costs, and status."
                    
                    st.session_state.show_bookings_form = False
                    execute_prompt_through_agent(prompt_text, "View Bookings", args)
        
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
                    
                    # Create prompt for the agent
                    prompt_text = f"""Generate a comprehensive summary for turf {turf_id} ({date_range}). Please:
1. Show turf details 
2. Show booking information
3. Check upcoming availability
4. Provide insights on booking patterns, popular time slots, revenue information, and recommendations for optimal booking times."""
                    
                    st.session_state.show_summary_form = False
                    execute_prompt_through_agent(prompt_text, "Booking Summary", args)
    
    # Display prompt results
    st.subheader("📨 Prompt Results")
    
    if st.session_state.prompt_messages:
        for i, message in enumerate(reversed(st.session_state.prompt_messages[-10:])):  # Show last 10
            with st.expander(f"🎯 {message['action']} - Result #{len(st.session_state.prompt_messages)-i}", expanded=True):
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
        # Reset form states
        for key in list(st.session_state.keys()):
            if key.startswith('show_') and key.endswith('_form'):
                del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    main()
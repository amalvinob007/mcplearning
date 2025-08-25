import streamlit as st
import sys
import os
from datetime import datetime, date, timedelta
import asyncio

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import synchronous wrappers and prompt processor
from sync_agent import get_sync_agent
from prompt_server import get_prompt

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
    .template-preview {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #007bff;
        margin: 10px 0;
        font-family: monospace;
        font-size: 0.9em;
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

class SyncPromptProcessor:
    """Synchronous wrapper for prompt processing"""
    
    @staticmethod
    def get_formatted_prompt(prompt_name: str, arguments: dict = None):
        """Get formatted prompt synchronously"""
        try:
            # Create new event loop for this operation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Get the formatted prompt
            prompt_result = loop.run_until_complete(get_prompt(prompt_name, arguments))
            
            # Extract the prompt text
            message = prompt_result.messages[0]
            formatted_prompt = message.content.text
            
            loop.close()
            return formatted_prompt
            
        except Exception as e:
            return f"Error getting prompt template: {str(e)}"

def execute_prompt_with_template(prompt_name: str, action_name: str, args: dict = None):
    """Execute a prompt using template first, then send to agent"""
    if not setup_agent():
        return
    
    with st.spinner(f"🔄 {action_name}..."):
        # Step 1: Get formatted prompt from template
        processor = SyncPromptProcessor()
        formatted_prompt = processor.get_formatted_prompt(prompt_name, args)
        
        if formatted_prompt.startswith("Error"):
            st.error(formatted_prompt)
            return
        
        # Step 2: Send formatted prompt to agent
        agent = get_sync_agent()
        result = agent.chat(formatted_prompt)
        
        # Step 3: Store result with template info
        st.session_state.prompt_messages.append({
            "type": "prompt_result",
            "action": action_name,
            "prompt_name": prompt_name,
            "args": args,
            "formatted_prompt": formatted_prompt,
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
    """Smart prompts interface using prompt templates"""
    st.header("🎯 Smart Prompts - Using Template System")
    
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
            execute_prompt_with_template("list-turfs", "List All Turfs")
        
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
                
                # Preview the template that will be generated
                preview_args = {
                    "turf_id": str(turf_id),
                    "date": check_date.strftime("%Y-%m-%d"),
                    "preferred_time": preferred_time
                }
                
                with st.expander("🔍 Preview Template", expanded=False):
                    processor = SyncPromptProcessor()
                    preview_prompt = processor.get_formatted_prompt("check-availability", preview_args)
                    st.markdown(f'<div class="template-preview">{preview_prompt}</div>', unsafe_allow_html=True)
                
                if st.form_submit_button("Check Availability"):
                    args = {
                        "turf_id": str(turf_id),
                        "date": check_date.strftime("%Y-%m-%d"),
                        "preferred_time": preferred_time
                    }
                    
                    st.session_state.show_availability_form = False
                    execute_prompt_with_template("check-availability", "Check Availability", args)
        
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
                
                # Preview template
                preview_args = {
                    "turf_id": str(turf_id),
                    "customer_name": customer_name,
                    "customer_phone": customer_phone,
                    "booking_date": booking_date.strftime("%Y-%m-%d"),
                    "start_time": start_time.strftime("%H:%M"),
                    "end_time": end_time.strftime("%H:%M")
                }
                
                if customer_name and customer_phone:
                    with st.expander("🔍 Preview Template", expanded=False):
                        processor = SyncPromptProcessor()
                        preview_prompt = processor.get_formatted_prompt("make-booking", preview_args)
                        st.markdown(f'<div class="template-preview">{preview_prompt}</div>', unsafe_allow_html=True)
                
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
                        
                        st.session_state.show_booking_form = False
                        execute_prompt_with_template("make-booking", "Make Booking", args)
                    else:
                        st.error("Please fill in customer name and phone number")
        
        # View Bookings Form
        if st.session_state.get('show_bookings_form', False):
            with st.form("bookings_form"):
                st.write("**📅 View Bookings (with filters)**")
                date_filter = st.date_input("Filter by Date (optional)", value=None)
                turf_filter = st.number_input("Filter by Turf ID (optional)", min_value=0, value=0)
                
                # Preview template
                preview_args = {}
                if date_filter:
                    preview_args["date_filter"] = date_filter.strftime("%Y-%m-%d")
                if turf_filter > 0:
                    preview_args["turf_filter"] = str(turf_filter)
                
                if preview_args:
                    with st.expander("🔍 Preview Template", expanded=False):
                        processor = SyncPromptProcessor()
                        preview_prompt = processor.get_formatted_prompt("view-bookings", preview_args)
                        st.markdown(f'<div class="template-preview">{preview_prompt}</div>', unsafe_allow_html=True)
                
                if st.form_submit_button("View Bookings"):
                    args = {}
                    if date_filter:
                        args["date_filter"] = date_filter.strftime("%Y-%m-%d")
                    if turf_filter > 0:
                        args["turf_filter"] = str(turf_filter)
                    
                    st.session_state.show_bookings_form = False
                    execute_prompt_with_template("view-bookings", "View Bookings", args)
        
        # Summary Form
        if st.session_state.get('show_summary_form', False):
            with st.form("summary_form"):
                st.write("**📊 Booking Summary**")
                turf_id = st.number_input("Turf ID for Summary", min_value=1, value=1)
                date_range = st.selectbox("Date Range", 
                    ["current", "this_week", "next_week", "this_month", "next_month"])
                
                # Preview template
                preview_args = {
                    "turf_id": str(turf_id),
                    "date_range": date_range
                }
                
                with st.expander("🔍 Preview Template", expanded=False):
                    processor = SyncPromptProcessor()
                    preview_prompt = processor.get_formatted_prompt("booking-summary", preview_args)
                    st.markdown(f'<div class="template-preview">{preview_prompt}</div>', unsafe_allow_html=True)
                
                if st.form_submit_button("Generate Summary"):
                    args = {
                        "turf_id": str(turf_id),
                        "date_range": date_range
                    }
                    
                    st.session_state.show_summary_form = False
                    execute_prompt_with_template("booking-summary", "Booking Summary", args)
    
    # Display prompt results with template information
    st.subheader("📨 Prompt Results")
    
    if st.session_state.prompt_messages:
        for i, message in enumerate(reversed(st.session_state.prompt_messages[-10:])):  # Show last 10
            with st.expander(f"🎯 {message['action']} - Result #{len(st.session_state.prompt_messages)-i}", expanded=True):
                
                # Show template information
                st.write("**🎯 Template Used:**", f"`{message.get('prompt_name', 'N/A')}`")
                
                if message.get('args'):
                    st.write("**📝 Parameters:**")
                    st.json(message['args'])
                
                # Show formatted prompt
                if message.get('formatted_prompt'):
                    with st.expander("📋 Generated Prompt", expanded=False):
                        st.markdown(f'<div class="template-preview">{message["formatted_prompt"]}</div>', 
                                   unsafe_allow_html=True)
                
                st.write("**🤖 Agent Response:**")
                st.markdown(f'<div class="prompt-message">{message["content"]}</div>', 
                           unsafe_allow_html=True)
    else:
        st.info("👆 Use the buttons above to perform quick actions using prompt templates!")
    
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
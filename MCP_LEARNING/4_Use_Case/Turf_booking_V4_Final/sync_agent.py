import asyncio
import os
import threading
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SyncTurfAgent:
    """Synchronous wrapper for the turf booking agent"""
    
    def __init__(self):
        self.agent = None
        self.client = None
        self.initialized = False
        self._loop = None
        self._thread = None
        self._setup_lock = threading.Lock()
        
    def _run_event_loop(self):
        """Run the event loop in a separate thread"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_forever()
        except Exception as e:
            print(f"Event loop error: {e}")
        finally:
            self._loop.close()
    
    def setup(self):
        """Setup the agent synchronously"""
        with self._setup_lock:
            if self.initialized:
                return True
                
            try:
                print("🔄 Initializing Turf Booking Agent...")
                
                # Start the event loop in a separate thread if not already running
                if self._thread is None or not self._thread.is_alive():
                    self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
                    self._thread.start()
                    
                    # Wait for the loop to be ready with timeout
                    timeout = 10
                    start_time = threading.get_ident()
                    while self._loop is None and timeout > 0:
                        threading.Event().wait(0.1)
                        timeout -= 0.1
                    
                    if self._loop is None:
                        print("❌ Failed to start event loop")
                        return False
                
                # Setup the agent
                print("🤖 Setting up agent components...")
                future = asyncio.run_coroutine_threadsafe(self._async_setup(), self._loop)
                success = future.result(timeout=30)
                
                if success:
                    self.initialized = True
                    print("✅ Agent setup completed successfully!")
                    return True
                else:
                    print("❌ Agent setup failed")
                    return False
                    
            except Exception as e:
                print(f"❌ Setup error: {e}")
                return False
    
    async def _async_setup(self):
        """Async setup method"""
        try:
            from turf_agent import setup_turf_agent
            print("📡 Connecting to MCP server...")
            self.agent, self.client = await setup_turf_agent()
            print("🔗 MCP client connected successfully")
            return True
        except Exception as e:
            print(f"❌ Async setup error: {e}")
            return False
    
    def chat(self, message: str) -> str:
        """Process a chat message synchronously"""
        if not self.initialized:
            setup_success = self.setup()
            if not setup_success:
                return "❌ Agent not initialized. Setup failed."
        
        try:
            print(f"💭 Processing message: {message[:100]}...")
            future = asyncio.run_coroutine_threadsafe(
                self._async_chat(message), 
                self._loop
            )
            response = future.result(timeout=120)  # Increased timeout for complex queries
            print("✅ Message processed successfully")
            return response
            
        except asyncio.TimeoutError:
            return "❌ Request timed out. Please try again with a simpler query."
        except Exception as e:
            print(f"❌ Chat error: {e}")
            return f"❌ Error: {str(e)}"
    
    async def _async_chat(self, message: str) -> str:
        """Async chat processing"""
        try:
            print("🔄 Invoking agent...")
            response = await self.agent.ainvoke(
                {"messages": [{"role": "user", "content": message}]}
            )
            
            # Get the last assistant message
            last_message = response["messages"][-1]
            print(f"📝 Response received: {len(last_message.content)} characters")
            return last_message.content
            
        except Exception as e:
            print(f"❌ Processing error: {e}")
            return f"❌ Processing error: {str(e)}"
    
    def process_prompt_template(self, prompt_name: str, arguments: dict = None) -> str:
        """Process a prompt template synchronously"""
        if not self.initialized:
            setup_success = self.setup()
            if not setup_success:
                return "❌ Agent not initialized. Setup failed."
        
        try:
            print(f"🎯 Processing prompt template: {prompt_name}")
            future = asyncio.run_coroutine_threadsafe(
                self._async_process_prompt(prompt_name, arguments), 
                self._loop
            )
            response = future.result(timeout=120)
            print("✅ Prompt template processed successfully")
            return response
            
        except asyncio.TimeoutError:
            return "❌ Prompt processing timed out. Please try again."
        except Exception as e:
            print(f"❌ Prompt processing error: {e}")
            return f"❌ Error: {str(e)}"
    
    async def _async_process_prompt(self, prompt_name: str, arguments: dict = None) -> str:
        """Async prompt processing"""
        try:
            # Import prompt processor
            from prompt_server import get_prompt
            
            print(f"📋 Getting prompt template: {prompt_name}")
            # Get the formatted prompt
            prompt_result = await get_prompt(prompt_name, arguments)
            
            # Extract the prompt text
            message = prompt_result.messages[0]
            formatted_prompt = message.content.text
            
            print(f"🔄 Sending formatted prompt to agent...")
            # Send to agent
            response = await self.agent.ainvoke(
                {"messages": [{"role": "user", "content": formatted_prompt}]}
            )
            
            # Get the last assistant message
            last_message = response["messages"][-1]
            return last_message.content
            
        except Exception as e:
            print(f"❌ Async prompt processing error: {e}")
            return f"❌ Prompt processing error: {str(e)}"
    
    def get_status(self) -> dict:
        """Get agent status"""
        return {
            "initialized": self.initialized,
            "thread_alive": self._thread.is_alive() if self._thread else False,
            "loop_running": self._loop is not None and not self._loop.is_closed() if self._loop else False
        }
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            print("🧹 Cleaning up agent resources...")
            
            if self._loop and not self._loop.is_closed():
                # Schedule client cleanup if client exists
                if self.client:
                    asyncio.run_coroutine_threadsafe(self.client.aclose(), self._loop)
                
                # Stop the event loop
                self._loop.call_soon_threadsafe(self._loop.stop)
            
            self.initialized = False
            print("✅ Cleanup completed")
            
        except Exception as e:
            print(f"❌ Cleanup error: {e}")

# Global instance
_sync_agent = None
_agent_lock = threading.Lock()

def get_sync_agent():
    """Get the global sync agent instance (singleton pattern)"""
    global _sync_agent
    with _agent_lock:
        if _sync_agent is None:
            _sync_agent = SyncTurfAgent()
        return _sync_agent

def reset_sync_agent():
    """Reset the global agent instance"""
    global _sync_agent
    with _agent_lock:
        if _sync_agent:
            _sync_agent.cleanup()
        _sync_agent = None

# Cleanup on module exit
import atexit
atexit.register(lambda: get_sync_agent().cleanup() if _sync_agent else None)
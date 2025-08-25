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
        
    def _run_event_loop(self):
        """Run the event loop in a separate thread"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()
    
    def setup(self):
        """Setup the agent synchronously"""
        if self.initialized:
            return True
            
        try:
            # Start the event loop in a separate thread
            self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
            self._thread.start()
            
            # Wait for the loop to be ready
            while self._loop is None:
                threading.Event().wait(0.01)
            
            # Setup the agent
            future = asyncio.run_coroutine_threadsafe(self._async_setup(), self._loop)
            success = future.result(timeout=30)
            
            if success:
                self.initialized = True
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Setup error: {e}")
            return False
    
    async def _async_setup(self):
        """Async setup method"""
        try:
            from turf_agent import setup_turf_agent
            self.agent, self.client = await setup_turf_agent()
            return True
        except Exception as e:
            print(f"❌ Async setup error: {e}")
            return False
    
    def chat(self, message: str) -> str:
        """Process a chat message synchronously"""
        if not self.initialized:
            return "❌ Agent not initialized. Please setup first."
        
        try:
            future = asyncio.run_coroutine_threadsafe(
                self._async_chat(message), 
                self._loop
            )
            response = future.result(timeout=60)
            return response
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    async def _async_chat(self, message: str) -> str:
        """Async chat processing"""
        try:
            response = await self.agent.ainvoke(
                {"messages": [{"role": "user", "content": message}]}
            )
            
            # Get the last assistant message
            last_message = response["messages"][-1]
            return last_message.content
            
        except Exception as e:
            return f"❌ Processing error: {str(e)}"
    
    def cleanup(self):
        """Cleanup resources"""
        if self._loop and not self._loop.is_closed():
            self._loop.call_soon_threadsafe(self._loop.stop)
        
        if self.client:
            # Schedule client cleanup
            if self._loop:
                asyncio.run_coroutine_threadsafe(self.client.aclose(), self._loop)

# Global instance
sync_agent = SyncTurfAgent()

def get_sync_agent():
    """Get the global sync agent instance"""
    return sync_agent
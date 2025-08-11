"""
Test Layout Architect through the main application.

This script starts the server and tests the full flow.
"""

import asyncio
import aiohttp
import json
import time
import os
import sys

# Add parent directory to path to import from src if needed
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_full_flow():
    """Test the complete flow from greeting to layout generation."""
    
    print("=== Testing Layout Architect with Main Application ===\n")
    print("⚠️  Make sure main.py is running on port 8000\n")
    
    # WebSocket URL
    ws_url = "ws://localhost:8000/ws"
    
    # Test session
    session_id = f"test_layout_{int(time.time())}"
    user_id = "test_user"
    
    try:
        # Connect to WebSocket
        session = aiohttp.ClientSession()
        ws = await session.ws_connect(f"{ws_url}?session_id={session_id}&user_id={user_id}")
        
        print("✅ Connected to WebSocket\n")
        
        # Helper to send and receive
        async def send_and_receive(message, expected_count=1):
            await ws.send_json(message)
            responses = []
            for _ in range(expected_count):
                msg = await ws.receive()
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    responses.append(data)
                    print(f"📥 Received: {data['type']}")
                    if data['type'] == 'theme_update':
                        print(f"   Theme: {data['payload']['theme_name']}")
                    elif data['type'] == 'slide_update':
                        slides = data['payload'].get('slides', [])
                        if slides:
                            print(f"   Slide: {slides[0]['slide_id']}")
            return responses
        
        # 1. Initial greeting
        print("1. Sending initial request...")
        await send_and_receive({
            "type": "user_input",
            "data": {
                "text": "I need a presentation about AI in healthcare"
            }
        })
        
        # 2. Answer clarifying questions
        print("\n2. Answering clarifying questions...")
        await send_and_receive({
            "type": "user_input",
            "data": {
                "text": "Target audience: Healthcare executives. Duration: 15 minutes. Goal: Show AI benefits and implementation path. Include real examples and ROI data."
            }
        })
        
        # 3. Accept the plan (triggers GENERATE_STRAWMAN)
        print("\n3. Accepting the plan...")
        await asyncio.sleep(1)  # Wait for plan
        await send_and_receive({
            "type": "user_input",
            "data": {
                "text": "Yes, that looks perfect, go ahead."  # Natural language that intent router expects
            }
        }, expected_count=2)  # Expecting status + chat messages
        
        # 4. Wait for strawman generation
        print("\n4. Waiting for strawman generation (this takes 30-40 seconds)...")
        strawman_start = time.time()
        strawman_received = False
        strawman_messages = []
        
        # Wait up to 45 seconds for strawman
        while time.time() - strawman_start < 45:
            try:
                msg = await asyncio.wait_for(ws.receive(), timeout=1.0)
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    elapsed = int(time.time() - strawman_start)
                    print(f"   [{elapsed}s] 📥 Received: {data['type']}")
                    
                    # Check for strawman in different message types
                    if data['type'] == 'chat_message':
                        # Check if this contains the actual strawman
                        content = data.get('payload', {}).get('content', '')
                        if isinstance(content, dict) and content.get('type') == 'PresentationStrawman':
                            print(f"   ✅ Strawman received with {len(content.get('slides', []))} slides!")
                            strawman_received = True
                            strawman_messages.append(data)
                        elif 'strawman' in str(data).lower():
                            print("   📝 Strawman-related message")
                            strawman_messages.append(data)
                    elif data['type'] == 'action_request':
                        print("   ✅ Action requested (strawman ready)")
                        strawman_received = True
                        break
                    elif data['type'] == 'status_update':
                        status = data.get('payload', {})
                        print(f"   📊 Status: {status.get('status')} - {status.get('text')}")
                        if status.get('status') == 'complete':
                            print("   ✅ Generation complete")
                            strawman_received = True
                            break
            except asyncio.TimeoutError:
                # Show we're still waiting
                if int(time.time() - strawman_start) % 5 == 0:
                    print(f"   ⏳ Still waiting... ({int(time.time() - strawman_start)}s)")
                continue
        
        if not strawman_received:
            print(f"   ❌ No strawman received after {int(time.time() - strawman_start)} seconds!")
            print("   🔍 Messages received during wait:")
            for msg in strawman_messages[-5:]:  # Show last 5 messages
                print(f"      - {msg['type']}")
        
        # 5. Accept the strawman (triggers LAYOUT_GENERATION)
        if strawman_received:
            print("\n5. Accepting strawman (triggers Layout Architect)...")
            await ws.send_json({
                "type": "user_input",
                "data": {
                    "text": "Looks good, we're done. Let's proceed with layout generation."  # Natural language that intent router expects
                }
            })
        else:
            print("\n5. ❌ Cannot accept strawman - none was generated!")
            print("   Test stopping here to avoid false results.")
            await ws.close()
            await session.close()
            return
        
        # Collect Layout Architect messages
        print("\n6. Receiving Layout Architect updates...")
        layout_messages = []
        theme_received = False
        slides_received = 0
        
        # Read messages for up to 30 seconds
        start_time = time.time()
        while time.time() - start_time < 30:
            try:
                msg = await asyncio.wait_for(ws.receive(), timeout=1.0)
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    layout_messages.append(data)
                    print(f"   📨 Received {data['type']} message")
                    
                    try:
                        if data['type'] == 'theme_update':
                            theme_received = True
                            print(f"   ✅ Theme received: {data['payload']['theme_name']}")
                        
                        elif data['type'] == 'slide_update':
                            slides = data['payload'].get('slides', [])
                            slides_received += len(slides)
                            for slide in slides:
                                try:
                                    # Look for structure_preference instead of layout
                                    structure = slide.get('structure_preference', 'No structure specified')
                                    print(f"   ✅ Slide {slide['slide_number']}: {slide['slide_type']} - {structure}")
                                except KeyError as e:
                                    print(f"   ❌ Error accessing slide field: {e}")
                                    print(f"   📋 Slide data keys: {list(slide.keys())}")
                                    print(f"   📋 Full slide data: {json.dumps(slide, indent=2)[:500]}...")
                        
                        elif data['type'] == 'status_update':
                            status = data['payload']
                            print(f"   📊 Status: {status['status']} - {status['text']}")
                            if status['status'] == 'complete':
                                break
                                
                    except Exception as e:
                        print(f"   ❌ Error processing message type {data.get('type', 'unknown')}: {e}")
                        print(f"   📋 Message data: {json.dumps(data, indent=2)[:500]}...")
                            
            except asyncio.TimeoutError:
                continue
        
        # Summary
        print(f"\n📈 Layout Architect Results:")
        print(f"   Strawman generated: {'✅' if strawman_received else '❌'}")
        print(f"   Theme received: {'✅' if theme_received else '❌'}")
        print(f"   Slides processed: {slides_received}")
        print(f"   Total Layout Architect messages: {len(layout_messages)}")
        
        # Show message types breakdown
        message_types = {}
        for msg in layout_messages:
            msg_type = msg.get('type', 'unknown')
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        print(f"\n📊 Message breakdown:")
        for msg_type, count in message_types.items():
            print(f"   - {msg_type}: {count}")
        
        await ws.close()
        await session.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure:")
        print("1. main.py is running")
        print("2. Your .env file has all required credentials")
        print("3. The database migrations have been run")
        print("4. Check server logs for detailed debug output")


if __name__ == "__main__":
    print("Starting full flow test...\n")
    asyncio.run(test_full_flow())
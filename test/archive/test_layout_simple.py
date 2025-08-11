#!/usr/bin/env python3
"""Simple test to debug theme sending."""

import asyncio
import aiohttp
import json
import time


async def test_simple():
    """Test just the layout architect trigger."""
    
    print("=== Simple Layout Architect Test ===\n")
    
    ws_url = "ws://localhost:8000/ws"
    session_id = f"test_simple_{int(time.time())}"
    user_id = "test_user"
    
    try:
        session = aiohttp.ClientSession()
        ws = await session.ws_connect(f"{ws_url}?session_id={session_id}&user_id={user_id}")
        
        print("✅ Connected\n")
        
        # Send all messages needed to reach layout generation
        messages = [
            {"type": "user_input", "data": {"text": "I need a presentation about cloud computing"}},
            {"type": "user_input", "data": {"text": "For developers, 20 minutes, focus on AWS services"}},
            {"type": "user_input", "data": {"text": "Yes, that looks perfect, go ahead."}},
        ]
        
        for i, msg in enumerate(messages):
            print(f"Sending message {i+1}...")
            await ws.send_json(msg)
            await asyncio.sleep(2)  # Wait between messages
        
        # Wait for strawman
        print("\nWaiting for strawman generation...")
        await asyncio.sleep(10)
        
        # Accept strawman to trigger layout
        print("\nTriggering Layout Architect...")
        await ws.send_json({
            "type": "user_input",
            "data": {"text": "Looks good, we're done. Let's proceed with layout generation."}
        })
        
        # Collect all messages
        print("\nCollecting messages for 20 seconds...")
        messages = []
        start_time = time.time()
        
        while time.time() - start_time < 20:
            try:
                msg = await asyncio.wait_for(ws.receive(), timeout=1.0)
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    messages.append(data)
                    print(f"📨 {data['type']}: ", end="")
                    
                    if data['type'] == 'theme_update':
                        print(f"Theme = {data['payload']['theme_name']}")
                    elif data['type'] == 'slide_update':
                        slides = data['payload'].get('slides', [])
                        print(f"{len(slides)} slides")
                    elif data['type'] == 'status_update':
                        print(f"{data['payload']['status']} - {data['payload']['text']}")
                    else:
                        print("✓")
                        
            except asyncio.TimeoutError:
                continue
        
        # Summary
        print(f"\n📊 Total messages received: {len(messages)}")
        theme_msgs = [m for m in messages if m['type'] == 'theme_update']
        slide_msgs = [m for m in messages if m['type'] == 'slide_update']
        print(f"   Theme updates: {len(theme_msgs)}")
        print(f"   Slide updates: {len(slide_msgs)}")
        
        await ws.close()
        await session.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_simple())
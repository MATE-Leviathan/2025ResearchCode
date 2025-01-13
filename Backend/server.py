'''
Written by Larry Zhao
Research robot code using websockets.
'''

#just in case:
#allow incoming connections to port 8765: sudo ufw allow 8765
#find the IP under the active network: ifconfig or ip a

import asyncio
import websockets
import json
import cv2
import base64
import sys
from control import control_rov, get_status
from sensors import get_sensor_data

# Receive controller input
async def receive_controls(websocket):
    robot_controls = {}
    try:
        while True:
            # Receive and parse JSON input
            data = await websocket.recv()
            commands = json.loads(data)
            robot_controls.update(commands)
            
            # Clear the line and print updated controls
            # sys.stdout.write("\033[2K\r")  # Clear the line
            # sys.stdout.write(f"\rCurrent Controls: {robot_controls}")  # Overwrite with new text
            # sys.stdout.flush()

            # Control ROV using recieved controls
            control_rov(robot_controls)
            
            await asyncio.sleep(0.1) # Update every 100ms  
            
    except websockets.ConnectionClosed:
        print("Client disconnected.")

# Stream video frames
async def send_video(websocket):
    cap = cv2.VideoCapture(0)  # Use the robot's camera 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("no camera :(")
            break
        _, buffer = cv2.imencode('.jpg', frame)  # Encode the frame as JPEG
        frame_data = base64.b64encode(buffer).decode('utf-8')  # Convert to Base64
        await websocket.send(json.dumps({"frame": frame_data}))
        await asyncio.sleep(0.016)  # some fps

# Send sensor data and robot status
async def send_data(websocket):
    while True:
        data = get_sensor_data()
        data.update(get_status())
        
        await websocket.send(json.dumps(data))
        await asyncio.sleep(0.1)  # Update every 100ms        

# Handle incoming requests
async def server_handler(websocket): # can take a path argument, but we don't need
    # Run tasks
    await asyncio.gather(
        send_data(websocket), 
        send_video(websocket),
        receive_controls(websocket),
        )

async def main():
    # Start WebSocket Server
    async with websockets.serve(server_handler, "0.0.0.0", 8765):
        print("Websockets Server Started")
        await asyncio.Future() # run forever

# Modern event loop handling
asyncio.run(main())
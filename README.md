# Kracken Research Code V2
Controls the robot using websockets rather than http requests to reduce latency\
Written by: Larry Zhao

## Instructions to Set Up:
### Frontend:
(This is run on your computer)
1. Install Node.js and npm
2. Open the ResearchDashboard2 folder in your Terminal (can be in VS Code)
3. Run `npm i` to install necessary libraries
4. Run `npm run dev` to open the dashboard
5. Click one of the displayed ports (Ex: "[ws://localhost:8765](ws://localhost:8765)")

### Backend:
(This is run on the Jetson)
1. (Optional) Create a virtual environment
   1. Open the Backend folder in your Terminal
   2. Run `python3 -m venv venv` to create a virtual environment called venv
   3. Run `source venv/bin/activate` to activate the virtual environment
   4. You should now see `(venv)` on the left side of your Terminal
2. Run `pip install -r requirements.txt` to install dependencies
3. Run `python3 server.py` to start the server

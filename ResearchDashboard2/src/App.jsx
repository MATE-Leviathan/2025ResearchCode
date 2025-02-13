import { useEffect, useState, useRef } from 'react'
import './App.css'
//import Chart from 'react-apexcharts';

function App() {
  const ip = "ws://10.50.2.100:8765/"; //ip of jetson wifi
  //const ip = "ws://10.42.0.1:8765/"; //ip of jetson ethernet
  //const ip = "ws://localhost:8765"; //local computer ip

  const webSocketRef = useRef(null);
  const [sensorData, setSensorData] = useState({});
  const [frame, setFrame] = useState(null);
  const [rovStatus, setRovStatus] = useState({});
  const [gamepadState, setGamepadState] = useState({});

  const [jetStatus, setJetStatus] = useState("Jetson Disconnected");
  const [conStatus, setConStatus] = useState("Controller Disconnected");
  const [jetStatusColor, setJetStatusColor] = useState("red");
  const [conStatusColor, setConStatusColor] = useState("red");

  useEffect(() => { // establish connection with jetson + receive data
    let retryTimeout;
  
    const connectWebSocket = () => {
      const socket = new WebSocket(ip);
      socket.binaryType = "blob"; // Expect binary data for frames
      webSocketRef.current = socket;
  
      socket.onopen = () => {
        console.log("WebSocket Connected");
        setJetStatus("Jetson Connected");
        setJetStatusColor("green");
        clearTimeout(retryTimeout);
      };
      socket.onerror = (error) => {
        console.error("WebSocket Error:", error);
        setJetStatus("Jetson Error");
        setJetStatusColor("red");
      };
      socket.onclose = () => {
        console.log("WebSocket Disconnected");
        setJetStatus("Jetson Disconnected");
        setJetStatusColor("red");
        retryTimeout = setTimeout(connectWebSocket, 3000); // Retry after 3 seconds
      };
      socket.onmessage = (message) => {
        if (typeof message.data === "string") {
          // JSON sensor data
          try{
            const data = JSON.parse(message.data);
            console.log(data);
            if ('sensor' in data) setSensorData(data.sensor);
            //if ('frame' in data) setFrame(`data:image/jpeg;base64,${data.frame}`);
            if ('status' in data) setRovStatus(data.status);
          } catch (error) {
            console.error("Error parsing JSON:", error);
          }
        }
        else {
          // Binary image frame
          const blob = message.data;
          const newUrl = URL.createObjectURL(blob);

          // Revoke the previous URL to prevent memory leaks
          if (window.lastFrameUrl) {
              URL.revokeObjectURL(window.lastFrameUrl);
          }
          window.lastFrameUrl = newUrl;
          
          setFrame(newUrl);
        }
      };
    };
  
    connectWebSocket();
  
    return () => {
      clearTimeout(retryTimeout);
      webSocketRef.current?.close();
    };
  }, [ip]);

  useEffect(() => { // sends input
    let lastSendTime = 0;
    const handleGamepadInput = () => {
      const gamepads = navigator.getGamepads();
      const gamepad = gamepads[0]; // Assuming the first connected gamepad
      if (gamepad) {
        setConStatus("Controller Connected"); // to optimize, should prob find a way to not change this every frame
        setConStatusColor("green"); // this might be getting rerendered every frame, which is unneeded
        const state = {
          axes: [...gamepad.axes], // Joystick positions
          buttons: gamepad.buttons.map((button) => button.pressed), // Button states
        };
        setGamepadState(state);
        const now = Date.now();
        // Send gamepad data via WebSocket
        if (webSocketRef.current && webSocketRef.current?.readyState === WebSocket.OPEN && now - lastSendTime > 100) {
          webSocketRef.current?.send(JSON.stringify(state));
          lastSendTime = now;
        }
      } else {
        setConStatus("Controller Disconnected");
        setConStatusColor("red");
      }
      requestAnimationFrame(handleGamepadInput);
    };
    handleGamepadInput(); // Start the gamepad polling loop
  }, []);

  useEffect(()=>{ //rollpitchline and yawline
    if(document.getElementById("yawLine")){
      document.getElementById("yawLine").style.rotate = (((sensorData?.yaw)?(sensorData.yaw):0)+90) + "deg"
      console.log((((sensorData?.yaw)?(sensorData.yaw):0)+90) + "deg")
    }
    if(document.getElementById("rpline")){
      document.getElementById("rpline").style.rotate = ((sensorData?.roll)?(sensorData.roll):0) + "deg"
      document.getElementById("rpline").style.translate = "0px " + (((sensorData?.pitch)?(sensorData.pitch):0)-70) + "px"
      console.log("0px " + (((sensorData?.pitch)?(sensorData.pitch):0)-70) + "px")
    }
  }, [sensorData?.roll, sensorData?.pitch, sensorData?.yaw])
  

  return ( //CSS is a mess, but it works (kinda)
<>
  <div className='cardGrid'>
    <div className="card" style={{width: "62vw", height: "95vh", marginLeft: "24px"}}>  
    <div>
      <h3 style={{marginLeft:"1vw"}}>Camera Stream #1</h3>
      <img 
        src={frame} 
        alt="Camera Frame"
        width="auto"
        height="112%"
        style={{borderRadius: "5px", marginLeft: "17%", marginTop: "-40%"}}
      ></img>
    </div>
    <div className="container" style={{position: "absolute", backgroundColor: "rgba(0,0,0,0)", bottom: "0px", left: "50px"}}>
      <div className="rpcompass" style={{backgroundColor: "rgba(0,0,0,0)", marginLeft: "0px", marginRight: "3%", marginBottom: "40px"}}><div className="rollpitchtick1"></div><div className="rollpitchtick2"></div><div className="rollpitchtick3"></div><div className="rollpitchtick4"></div><div className="rollpitchtick5"></div><div className="rollpitchtick6"></div><div className="rollpitchtick7"><div className="rollpitchLine" id="rpline"></div></div><small className="depth">Depth: {sensorData?.depth?Math.round(sensorData?.depth):"00"} ft</small></div>
      <p style={{marginLeft: "10px", height: "12px", marginTop: "150px"}}>Temperature: {sensorData?.external?.temp?Math.round(sensorData?.exttemp*100)/100:"00"} °F</p>
      <p style={{marginLeft: "80px", height: "12px", marginTop: "150px"}}>Barometric Pressure: {sensorData?.pressure?Math.round(sensorData?.pressure*100)/100:"00"} psi</p>
      <p style={{marginLeft: "80px", height: "12px", marginTop: "150px"}}>IMU Temp: {sensorData?.imutemp?sensorData?.imutemp:"00"} °F</p>
      <div className="yawcompass" style={{backgroundColor: "rgba(0,0,0,0)", marginLeft: "3%", marginRight: "0px", position: "absolute", bottom: "40px", right: "40vw"}}><div className="yawLine" id="yawLine"></div></div>
    </div>
    </div>

    <div className="card" style={{width: "34.5vw", height: "95vh", position: "absolute", right: "22px", top: "22px"}}>
      <div style={{marginLeft: "1vw"}}>
      <div className='status'>
        <h3 id='jetStatus' style={{color: jetStatusColor, marginRight: "15px"}}>{jetStatus}</h3>
        <h3 id='conStatus' style={{color: conStatusColor}}>{conStatus}</h3>
      </div>
      <div>
        <h3>Controller Input Display</h3>
        <div className="controller">
          <div className="buttons">
            {gamepadState.buttons?.map((pressed, index) => (
              <div
                key={index}
                className={`button ${pressed ? "pressed" : ""}`}
                style={{
                  width: "50px",
                  height: "50px",
                  display: "inline-block",
                  margin: "5px",
                  textAlign: "center",
                  lineHeight: "50px",
                  border: "2px solid #333",
                  borderRadius: "10px",
                  backgroundColor: pressed ? "#4caf50" : "#f0f0f0",
                  transition: "background-color 0.3s"
                }}
              >
                B{index}
              </div>
            ))}
          </div>
          <div className="axes" style={{ marginTop: "20px" }}>
            {gamepadState.axes?.map((value, index) => (
              <div key={index} style={{ margin: "10px" }}>
                Axis {index}: {value.toFixed(2)}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* <div>
        <h3>Sensor Display</h3>
        <h3 id='baroSensor'>Depth: {sensorData.depth}</h3>
        <h3 id='imuSensor'>Roll: {sensorData.roll}</h3>
        <h3 id='pHSensor'>Pitch: {sensorData.pitch}</h3>
        <h3 id='pHSensor'>Yaw: {sensorData.yaw}</h3>
        <h3 id='pHSensor'>ExtTemp: {sensorData.exttemp}</h3>
        <h3 id='pHSensor'>IMUTemp: {sensorData.imutemp}</h3>
      </div> */}

      <div>
        <h3>ROV Status</h3>
        <p id='zLock'>zLock: {rovStatus?.zlock?rovStatus?.zlock:"False"}</p>
        <p id='brightness'>Light Brightness: {rovStatus?.lights?rovStatus?.lights:"0"}</p>
      </div>
      </div>
    </div>
  </div>
</>
  )
}

export default App

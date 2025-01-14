'''
Written by Larry Zhao, Rohan Tyagi, Stephen Zhou, Everett Tucker, Romeer Dhillon
Research robot code modified from 2024 SRIP.
'''
# Importing libraries
import adafruit_bno055
import board
import busio
import time
import adafruit_pca9685
from adafruit_motor import servo
import math
import tsys01
import ms5837
import smbus2
from sensors import get_bar

# Initialize sensors
i2c_bus = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c_bus, address=0x41)
pca.frequency = 450
pca.channels[0].duty_cycles = 0xffff
imu = adafruit_bno055.BNO055_I2C(busio.I2C(board.SCL, board.SDA), address=0x28)
celsiusSensor = tsys01.TSYS01()
baroSensor = ms5837.MS5837_30BA()

# Setting median pulse widths, angles, and max throttle for heave
mpulse = 1370
mangle = 90 #middle angle
heaveStrength = 0.5

# Initialize thrusters
fr1 = servo.Servo(pca.channels[0], min_pulse = mpulse, max_pulse = 1900)
mr2 = servo.Servo(pca.channels[1], min_pulse = mpulse, max_pulse = 1900)
br3 = servo.Servo(pca.channels[2], min_pulse = mpulse, max_pulse = 1900)
bl4 = servo.Servo(pca.channels[3], min_pulse = mpulse, max_pulse = 1900)
ml5 = servo.Servo(pca.channels[4], min_pulse = mpulse, max_pulse = 1900)
fl6 = servo.Servo(pca.channels[5], min_pulse = mpulse, max_pulse = 1900)
fr1.angle = mangle
mr2.angle = mangle
br3.angle = mangle
bl4.angle = mangle
ml5.angle = mangle
fl6.angle = mangle

# Initialize flashlights
flashlight1 = servo.Servo(pca.channels[6], min_pulse = 1100, max_pulse = 1900)
flashlight2 = servo.Servo(pca.channels[7], min_pulse = 1100, max_pulse = 1900)
flashlight3 = servo.Servo(pca.channels[8], min_pulse = 1100, max_pulse = 1900)
flashlight1.angle = 0
flashlight2.angle = 0
flashlight3.angle = 0

# Set robot status
prev_Controls = {"axes": [0.0] * 4, "buttons": [False] * 10}
lights = False
brightness = None
zLock = False
barTarget = None
slowmode = False # yet to be implemented

# Button binds
heaveUp = 7
heaveDown = 6
zLockButton = 4
lightsButton = 5

# Control the ROV based on controller input
def control_rov(robot_controls):
    global prev_Controls, lights, zLock, slowmode
    
    # turn controller input into percentage of max throttle
    X1 = round(robot_controls.get("axes", [0])[0] * 10) / 10
    Y1 = round(robot_controls.get("axes", [0])[1] * 10) / 10
    X2 = round(robot_controls.get("axes", [0])[2] * 10) / 10
    #Y2 = round(robot_controls.get("axes", [0])[3] * 10) / 10
    
    # strafing
    if X1 > 0 or Y1 > 0: 
        strafe(X1, -Y1) #not sure why y1 is negative
    
    # turning
    if X2 > 0:
        turn(X2)
        
    # heave
    if robot_controls.get("buttons", {})[heaveUp] ^ robot_controls.get("buttons", {})[heaveDown]:
        if robot_controls.get("buttons")[heaveUp]:
            heave(heaveStrength)
        else:
            heave(-heaveStrength)
            
    # toggle zLock
    if robot_controls.get("buttons", {})[zLockButton] and not prev_Controls.get("buttons", {})[zLockButton]:
        zLock = not zLock
    if zLock:
        zlock()
            
    # toggle lights using controller
    if robot_controls.get("buttons", {})[lightsButton] and not prev_Controls.get("buttons", {})[lightsButton]:
        lights = not lights
    if robot_controls.get("light", 0) > 0 or lights:
        if lights:
            level = 180
        else:
            level = int(robot_controls.get("light", 0))
        control_lights(level)
        
    # store current controls for next cycle
    prev_Controls = robot_controls

# Strafing logic
def strafe(x, y):
    theta = math.atan((float(y))/(float(x)+0.0000000000000001))*180/math.pi
    if theta < 0 and float(x) < 0:
        theta += 180
    if theta < 0 and float(y) < 0:
        theta += 360
    if float(x) < 0 and float(y) < 0:
        theta += 180
    mag = math.dist([0,0], [float(x),float(y)])
    print(180-(mag*90*math.sin((theta-45)*math.pi/180)+90))
    fr1.angle = 180-(mag*90*math.sin((theta-45)*math.pi/180)+90)
    br3.angle = 180-(mag*90*math.sin((theta-135)*math.pi/180)+90)
    bl4.angle = 180-(mag*90*math.sin((theta-225)*math.pi/180)+90)
    fl6.angle = 180-(mag*90*math.sin((theta+45)*math.pi/180)+90)

# Turning logic
def turn(X2):
    mag = int(float(X2)*90)+90
    fr1.angle = mag
    br3.angle = 180-mag
    bl4.angle = mag
    fl6.angle = 180-mag

# Heave(Up and Down) logic
def heave(mag):
    global zLock
    zLock = False
    z = int(float(mag)*90)+90
    mr2.angle = z
    ml5.angle = z

# Z Lock
def zlock(): # could add PID in future
    global barTarget
    barCurrent = get_bar()
    barChange = barTarget-barCurrent 
    mr2.angle = int(barChange*30)+90
    ml5.angle = int(barChange*30)+90

# Controls the level of brightness of the flashlights
def control_lights(level):
    global brightness
    brightness = level # updating status
    flashlight1.angle = level
    flashlight2.angle = level
    flashlight3.angle = level

# Returns status of ROV
def get_status():
    return {"status" : {
            "lights": brightness,
            "zLock": zLock,
            "slowmode": slowmode, 
        }}

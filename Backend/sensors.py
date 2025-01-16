'''
Written by Larry Zhao, Rohan Tyagi, Stephen Zhou, Everett Tucker, Romeer Dhillon
Research robot code modified from 2024 SRIP.
'''

# Importing libraries
import adafruit_bno055
import board
import busio
import adafruit_pca9685
import tsys01
import ms5837

# Initialize sensors
i2c_bus = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c_bus, address=0x41)
pca.frequency = 450
pca.channels[0].duty_cycles = 0xffff
imu = adafruit_bno055.BNO055_I2C(busio.I2C(board.SCL, board.SDA), address=0x28)
#celsiusSensor = tsys01.TSYS01()
baroSensor = ms5837.MS5837_30BA()

# Initialize temp and pressure sensors
#celsiusSensor.init()
#celsiusSensor.read()
baroSensor.init()
baroSensor.read()

# Returns all sensor data
def get_sensor_data():
    imutemp = imu.temperature
    exttemp = 0 #(celsiusSensor.temperature()+baroSensor.temperature(ms5837.UNITS_Centigrade))/2
    yaw = imu.euler[0]
    pitch = imu.euler[1]
    roll = imu.euler[2]
    pressure = baroSensor.pressure(ms5837.UNITS_psi)
    depth = baroSensor.depth()*3.28084
    
    return {"sensor" : {
            "imutemp": imutemp,
            "exttemp": exttemp,
            "yaw": yaw, 
            "pitch": pitch,
            "roll": roll,
            "pressure": pressure,
            "depth": depth,
        }}

# Returns pressure data
def get_bar():
    return round(baroSensor.pressure(ms5837.UNITS_psi)*100)/100

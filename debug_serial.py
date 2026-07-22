
import serial
print(f"Serial file: {serial.__file__}")
print(f"Dir serial: {dir(serial)}")
try:
    print(f"Serial.Serial: {serial.Serial}")
except AttributeError as e:
    print(f"Error: {e}")

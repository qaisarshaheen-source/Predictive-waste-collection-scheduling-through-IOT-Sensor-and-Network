import serial.tools.list_ports

def list_ports():
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No ports found! Is the Arduino plugged in?")
        return

    print("Available Ports:")
    for port in ports:
        print(f"- {port.device}: {port.description}")

if __name__ == "__main__":
    list_ports()

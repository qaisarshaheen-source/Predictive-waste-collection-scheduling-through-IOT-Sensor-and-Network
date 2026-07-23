import os

# Hardware Config
ARDUINO_PORT = os.getenv('ARDUINO_PORT', 'COM7')
BAUD_RATE = 9600
SERVO_COMMANDS = {
    'plastic': 'PLASTIC\n', 
    'paper': 'PAPER\n', 
    'glass': 'GLASS\n',
    'beep': 'BEEP\n'
}
FULL_THRESHOLD = 4  # cm (distance from sensor when full)
BIN_HEIGHT = 16     # cm (distance from sensor when empty/bottom)

# AI Config
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
WASTE_CLASSES = ['plastic', 'paper', 'wrapper', 'glass']

# App Config
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-prod')
DEBUG = False
HOST = '127.0.0.1'
PORT = 5000

# Email Config
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USERNAME = os.getenv('MAIL_USERNAME', )
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', )
MAIL_USE_TLS = True
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', )  # Ya 'rb0494259@gmail.com' for safety
ALERT_EMAIL_RECIPIENT = os.getenv('ALERT_EMAIL_RECIPIENT', )
ALERT_COOLDOWN = 60  # Seconds between alerts (Lowered for testing)

# Camera Defaults
CAMERA_AUTO_START = False
